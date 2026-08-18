import struct
import typing as t
from dataclasses import dataclass

import zstandard

from atproto_jetstream.exceptions import JetstreamDecodingError

_SEGMENT_MAGIC = b'jss0'
_HEADER_LEN = 256
_HEADER_VERSION = 1

#: Guards against a malformed length prefix claiming a huge block.
_MAX_BLOCK_BYTES = 1024 * 1024 * 256

#: `kind` column discriminator.
KIND_CREATE = 1
KIND_UPDATE = 2
KIND_DELETE = 3
KIND_IDENTITY = 4
KIND_ACCOUNT = 5
KIND_SYNC = 6

_COMMIT_OPERATION = {KIND_CREATE: 'create', KIND_UPDATE: 'update', KIND_DELETE: 'delete'}

#: Fixed-width columns, in the order they are laid out.
_FIXED_COLUMNS = (
    ('seq', 'Q'),
    ('witnessed_at', 'q'),
    ('indexed_at', 'q'),
    ('kind', 'B'),
    ('collection_len', 'B'),
    ('did_len', 'H'),
    ('rkey_len', 'B'),
    ('rev_len', 'B'),
    ('event_len', 'I'),
)

#: Variable-length columns, in the order they are concatenated.
_VARIABLE_COLUMNS = (
    ('collection', 'collection_len'),
    ('did', 'did_len'),
    ('rkey', 'rkey_len'),
    ('rev', 'rev_len'),
    ('payload', 'event_len'),
)


@dataclass
class SegmentHeader:
    """Fixed header of a sealed `.jss` segment."""

    version: int  #: Format version.
    block_count: int  #: Number of blocks.
    event_count: int  #: Number of events.
    footer_offset: int  #: Byte offset of the footer.
    block_index_offset: int  #: Byte offset of the block index.


@dataclass
class SegmentEvent:
    """One row of a segment block."""

    seq: int  #: Jetstream sequence number.
    witnessed_at: int  #: When Jetstream first saw the event, unix microseconds.
    indexed_at: int  #: Display timestamp, unix microseconds. 0 means fall back to `witnessed_at`.
    kind: int  #: Discriminator; see the KIND_* constants.
    did: str  #: Repo DID.
    collection: str  #: Collection NSID. Empty for non-commit kinds.
    rkey: str  #: Record key. Empty for non-commit kinds.
    rev: str  #: Repo rev. Empty for non-commit kinds.
    payload: t.Optional[bytes]  #: Raw record CBOR. Absent for deletes.

    @property
    def is_commit(self) -> bool:
        """:obj:`bool`: Whether the row is a record mutation."""
        return self.kind in _COMMIT_OPERATION

    @property
    def operation(self) -> t.Optional[str]:
        """:obj:`str`: `create`, `update` or `delete`, or :obj:`None` for non-commit kinds."""
        return _COMMIT_OPERATION.get(self.kind)

    @property
    def time_us(self) -> int:
        """:obj:`int`: Display timestamp in unix microseconds."""
        return self.indexed_at or self.witnessed_at


def read_sealed_header(data: bytes) -> SegmentHeader:
    """Parse the fixed 256-byte header of a sealed segment.

    Args:
        data: At least the first 256 bytes of the segment.

    Returns:
        :obj:`SegmentHeader`: Parsed header.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Not a sealed segment.
    """
    if len(data) < _HEADER_LEN:
        raise JetstreamDecodingError('Segment is shorter than its header')

    if data[:4] != _SEGMENT_MAGIC:
        raise JetstreamDecodingError('Bad segment magic')

    checksum, version, block_count, event_count = struct.unpack_from('<QHII', data, 4)
    if checksum == 0:
        # the header is only populated at seal time; an active segment is never served
        raise JetstreamDecodingError('Segment is active (unsealed)')

    if version != _HEADER_VERSION:
        raise JetstreamDecodingError(f'Unsupported segment version: {version}')

    (footer_offset,) = struct.unpack_from('<Q', data, 58)
    (block_index_offset,) = struct.unpack_from('<Q', data, 90)

    return SegmentHeader(
        version=version,
        block_count=block_count,
        event_count=event_count,
        footer_offset=footer_offset,
        block_index_offset=block_index_offset,
    )


def decompress_block(frame: bytes) -> bytes:
    """Decompress a stored block frame.

    Args:
        frame: Raw block frame, exactly as `getBlock` returns it.

    Returns:
        :obj:`bytes`: Decompressed block.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Undecodable or oversized block.
    """
    try:
        return zstandard.ZstdDecompressor().decompress(frame, max_output_size=_MAX_BLOCK_BYTES)
    except zstandard.ZstdError as e:
        raise JetstreamDecodingError('Could not decompress the block') from e


def decode_block(frame: bytes) -> t.List[SegmentEvent]:
    """Decode a stored block frame into rows.

    Args:
        frame: Raw block frame, exactly as `getBlock` returns it.

    Returns:
        :obj:`list` of :obj:`SegmentEvent`: Rows in sequence order.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Malformed block.
    """
    buf = decompress_block(frame)

    try:
        return _decode_columns(buf)
    except (struct.error, IndexError, UnicodeDecodeError) as e:
        raise JetstreamDecodingError('Malformed block') from e


def _decode_columns(buf: bytes) -> t.List[SegmentEvent]:
    (count,) = struct.unpack_from('<I', buf, 0)
    offset = 4

    columns: t.Dict[str, t.Sequence[int]] = {}
    for name, fmt in _FIXED_COLUMNS:
        columns[name] = struct.unpack_from(f'<{count}{fmt}', buf, offset)
        offset += struct.calcsize(fmt) * count

    blobs: t.Dict[str, t.List[bytes]] = {}
    for name, length_column in _VARIABLE_COLUMNS:
        values = []
        for length in columns[length_column]:
            values.append(buf[offset : offset + length])
            offset += length

        blobs[name] = values

    if offset != len(buf):
        raise JetstreamDecodingError(f'Block has {len(buf) - offset} trailing bytes')

    seq, kind = columns['seq'], columns['kind']
    witnessed_at, indexed_at = columns['witnessed_at'], columns['indexed_at']
    collection, did = blobs['collection'], blobs['did']
    rkey, rev, payload = blobs['rkey'], blobs['rev'], blobs['payload']

    return [
        SegmentEvent(
            seq=seq[i],
            witnessed_at=witnessed_at[i],
            indexed_at=indexed_at[i],
            kind=kind[i],
            did=did[i].decode('UTF-8'),
            collection=collection[i].decode('UTF-8'),
            rkey=rkey[i].decode('UTF-8'),
            rev=rev[i].decode('UTF-8'),
            payload=payload[i] or None,
        )
        for i in range(count)
    ]
