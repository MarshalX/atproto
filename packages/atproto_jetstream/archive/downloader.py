import asyncio
import time
import typing as t
from concurrent.futures import ThreadPoolExecutor

from atproto_client.client.async_raw import AsyncClientRaw
from atproto_client.client.raw import ClientRaw
from atproto_client.exceptions import RequestErrorBase

from atproto_jetstream.archive.planner import WorkUnit
from atproto_jetstream.archive.segment import SegmentEvent, decode_block, read_sealed_header
from atproto_jetstream.exceptions import JetstreamError

#: A whole segment is ~261 MB, far too much to hold in memory. Read it in Range slices.
SEGMENT_CHUNK_BYTES = 8 * 1024 * 1024

_HEADER_LEN = 256

#: Every block frame is prefixed with its compressed length.
_BLOCK_LENGTH_PREFIX = 8

DEFAULT_BLOCK_CONCURRENCY = 4

_TOO_MANY_REQUESTS = 429

#: Retry-After can be absent or unparseable; back off anyway rather than hammering the quota.
_DEFAULT_RETRY_AFTER_SEC = 5.0
_MAX_RETRY_AFTER_SEC = 300.0

#: A quota refills continuously, so waiting works; a wall of retries does not.
DEFAULT_MAX_QUOTA_WAITS = 10


def quota_retry_after(exception: BaseException) -> t.Optional[float]:
    """Seconds to wait if the request was rejected for exceeding the byte quota.

    Args:
        exception: Exception raised by an archive request.

    Returns:
        :obj:`float`: Delay to honour, or :obj:`None` if this was not a quota rejection.
    """
    if not isinstance(exception, RequestErrorBase) or not exception.args:
        return None

    response = exception.args[0]
    if getattr(response, 'status_code', None) != _TOO_MANY_REQUESTS:
        return None

    headers = getattr(response, 'headers', None) or {}
    try:
        delay = float(headers.get('retry-after', _DEFAULT_RETRY_AFTER_SEC))
    except (TypeError, ValueError):
        delay = _DEFAULT_RETRY_AFTER_SEC

    return min(max(delay, 0.0), _MAX_RETRY_AFTER_SEC)


class ByteMeter:
    """Counts downloaded bytes. Usage is metered in bytes, so callers need to see the spend."""

    def __init__(self) -> None:
        self._total = 0

    @property
    def total(self) -> int:
        """:obj:`int`: Bytes downloaded so far."""
        return self._total

    def add(self, count: int) -> None:
        self._total += count


def _auth_headers(api_key: t.Optional[str]) -> t.Dict[str, str]:
    if not api_key:
        return {}

    return {'Authorization': f'Bearer {api_key}'}


def _range_header(start: int, end: int) -> t.Dict[str, str]:
    return {'Range': f'bytes={start}-{end}'}


def iter_block_frames(segment: bytes) -> t.Iterator[bytes]:
    """Walk the length-prefixed block frames of a whole segment file.

    Args:
        segment: Complete segment bytes.

    Returns:
        Iterator of raw block frames.
    """
    header = read_sealed_header(segment)
    offset = _HEADER_LEN
    for _ in range(header.block_count):
        length = int.from_bytes(segment[offset : offset + _BLOCK_LENGTH_PREFIX], 'little')
        offset += _BLOCK_LENGTH_PREFIX
        yield segment[offset : offset + length]
        offset += length


class ArchiveDownloader:
    """Fetches planned work units and decodes them into rows.

    Args:
        base_url: HTTP origin of the jetstream host.
        api_key: Archive credential. Never used for anything else.
        meter: Byte meter to record the spend in.
    """

    def __init__(
        self,
        base_url: str,
        api_key: t.Optional[str],
        meter: ByteMeter,
        concurrency: int = DEFAULT_BLOCK_CONCURRENCY,
        max_quota_waits: int = DEFAULT_MAX_QUOTA_WAITS,
    ) -> None:
        self._client = ClientRaw(base_url=base_url)
        self._headers = _auth_headers(api_key)
        self._meter = meter
        self._concurrency = max(1, concurrency)
        self._max_quota_waits = max_quota_waits

    def _call(self, request: t.Callable[[], t.Any]) -> t.Any:
        """Run a request, waiting out byte-quota rejections rather than retrying blindly."""
        for _ in range(self._max_quota_waits + 1):
            try:
                return request()
            except Exception as e:
                delay = quota_retry_after(e)
                if delay is None:
                    raise

                time.sleep(delay)

        raise JetstreamError('Byte quota still exhausted after waiting')

    def plan_page(self, data: t.Dict[str, t.Any]) -> t.Any:
        return self._call(
            lambda: self._client.network.bsky.jetstream.plan_snapshot(t.cast('t.Any', data), headers=self._headers)
        )

    def fetch_block(self, segment: str, block_index: int) -> bytes:
        frame = self._call(
            lambda: self._client.network.bsky.jetstream.get_block(
                {'segment': segment, 'block_index': block_index}, headers=self._headers
            )
        )
        self._meter.add(len(frame))

        return frame

    def fetch_segment(self, name: str) -> bytes:
        """Download a whole segment in Range slices, so it never lands in memory at once."""
        chunks: t.List[bytes] = []
        start = 0
        while True:
            headers = {**self._headers, **_range_header(start, start + SEGMENT_CHUNK_BYTES - 1)}

            def fetch(headers: t.Dict[str, str] = headers) -> bytes:
                return self._client.network.bsky.jetstream.get_segment({'name': name}, headers=headers)

            chunk = self._call(fetch)
            if not chunk:
                break

            self._meter.add(len(chunk))
            chunks.append(chunk)
            if len(chunk) < SEGMENT_CHUNK_BYTES:
                break

            start += len(chunk)

        return b''.join(chunks)

    def rows(self, unit: WorkUnit) -> t.Iterator[SegmentEvent]:
        """Decode a work unit into rows, in seq order.

        Blocks download concurrently, since that is socket I/O and releases the GIL, but
        decode stays serial and emission stays in plan order.
        """
        if unit.is_whole_segment:
            for frame in iter_block_frames(self.fetch_segment(unit.segment)):
                yield from decode_block(frame)
            return

        blocks = list(unit.blocks or ())
        if len(blocks) == 1:
            yield from decode_block(self.fetch_block(unit.segment, blocks[0]))
            return

        with ThreadPoolExecutor(max_workers=self._concurrency) as pool:
            for frame in pool.map(lambda index: self.fetch_block(unit.segment, index), blocks):
                yield from decode_block(frame)


class AsyncArchiveDownloader:
    """Async twin of :obj:`ArchiveDownloader`."""

    def __init__(
        self,
        base_url: str,
        api_key: t.Optional[str],
        meter: ByteMeter,
        concurrency: int = DEFAULT_BLOCK_CONCURRENCY,
        max_quota_waits: int = DEFAULT_MAX_QUOTA_WAITS,
    ) -> None:
        self._client = AsyncClientRaw(base_url=base_url)
        self._headers = _auth_headers(api_key)
        self._meter = meter
        self._semaphore = asyncio.Semaphore(max(1, concurrency))
        self._max_quota_waits = max_quota_waits

    async def _call(self, request: t.Callable[[], t.Any]) -> t.Any:
        for _ in range(self._max_quota_waits + 1):
            try:
                return await request()
            except Exception as e:
                delay = quota_retry_after(e)
                if delay is None:
                    raise

                await asyncio.sleep(delay)

        raise JetstreamError('Byte quota still exhausted after waiting')

    async def plan_page(self, data: t.Dict[str, t.Any]) -> t.Any:
        return await self._call(
            lambda: self._client.network.bsky.jetstream.plan_snapshot(t.cast('t.Any', data), headers=self._headers)
        )

    async def fetch_block(self, segment: str, block_index: int) -> bytes:
        async with self._semaphore:
            frame = await self._call(
                lambda: self._client.network.bsky.jetstream.get_block(
                    {'segment': segment, 'block_index': block_index}, headers=self._headers
                )
            )
        self._meter.add(len(frame))

        return frame

    async def fetch_segment(self, name: str) -> bytes:
        chunks: t.List[bytes] = []
        start = 0
        while True:
            headers = {**self._headers, **_range_header(start, start + SEGMENT_CHUNK_BYTES - 1)}

            def fetch(headers: t.Dict[str, str] = headers) -> t.Any:
                return self._client.network.bsky.jetstream.get_segment({'name': name}, headers=headers)

            chunk = await self._call(fetch)
            if not chunk:
                break

            self._meter.add(len(chunk))
            chunks.append(chunk)
            if len(chunk) < SEGMENT_CHUNK_BYTES:
                break

            start += len(chunk)

        return b''.join(chunks)
