import typing as t
from copy import deepcopy

from atproto_client.client.async_raw import AsyncClientRaw
from atproto_client.client.raw import ClientRaw
from atproto_client.models.common import XrpcError
from atproto_subscription.websocket import AsyncWebsocketClient, WebsocketClient, WebsocketClientBase
from pydantic_core import from_json
from websockets.exceptions import InvalidStatus

from atproto_jetstream.compression import ZstdDecompression
from atproto_jetstream.exceptions import (
    JetstreamConsumerTooSlowError,
    JetstreamCursorTooOldError,
    JetstreamDecodingError,
    JetstreamError,
)
from atproto_jetstream.models import (
    ErrorFrame,
    MessageFrame,
    SubscribeEventsMessage,
    parse_frame,
    parse_subscribe_events_message,
)

#: v2 frames embed the record, so they are far larger than Firehose frames.
_MAX_MESSAGE_SIZE_BYTES = 1024 * 1024 * 32  # 32MB

_SUBPROTOCOL = 'xrpc.v1.json'

_CONSUMER_TOO_SLOW = 'ConsumerTooSlow'
_CURSOR_TOO_OLD = 'CursorTooOld'
_UNKNOWN_ZSTD_DICTIONARY = 'UnknownZstdDictionary'

_ZSTD_DICTIONARY_PARAM = 'zstdDictionary'

_WS_SCHEME_TO_HTTP = {'wss': 'https', 'ws': 'http'}

OnMessageCallback = t.Callable[[SubscribeEventsMessage], None]
AsyncOnMessageCallback = t.Callable[[SubscribeEventsMessage], t.Coroutine[t.Any, t.Any, None]]

OnCallbackErrorCallback = t.Callable[[BaseException], None]
AsyncOnCallbackErrorCallback = t.Callable[[BaseException], t.Coroutine[t.Any, t.Any, None]]


def _error_frame_to_exception(frame: ErrorFrame) -> JetstreamError:
    xrpc_error = XrpcError(frame.error, frame.message)
    if frame.error == _CONSUMER_TOO_SLOW:
        return JetstreamConsumerTooSlowError(xrpc_error)

    return JetstreamError(xrpc_error)


def _parse_xrpc_error(body: t.Optional[bytes]) -> t.Optional[XrpcError]:
    if not body:
        return None

    try:
        parsed = from_json(body)
    except ValueError:
        return None

    if not isinstance(parsed, dict) or 'error' not in parsed:
        return None

    return XrpcError(parsed['error'], parsed.get('message'))


def _rejected_handshake_to_exception(exception: InvalidStatus) -> t.Optional[JetstreamError]:
    """Map a pre-upgrade rejection to a fatal error, or :obj:`None` if it is worth retrying."""
    response = exception.response
    if not 400 <= response.status_code < 500:
        return None

    xrpc_error = _parse_xrpc_error(getattr(response, 'body', None))
    if xrpc_error is not None and xrpc_error.error == _CURSOR_TOO_OLD:
        return JetstreamCursorTooOldError(xrpc_error)

    return JetstreamError(xrpc_error if xrpc_error is not None else exception)


class _JetstreamClientMixin(WebsocketClientBase):
    """Jetstream v2 framing, cursor tracking, and deduplication."""

    _error_class = JetstreamError

    def __init__(
        self,
        method: str,
        base_uri: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        recv_timeout: t.Optional[float] = None,
        compress: bool = True,
    ) -> None:
        super().__init__(
            method,
            base_uri,
            deepcopy(params) if params else params,
            recv_timeout,
            max_message_size_bytes=_MAX_MESSAGE_SIZE_BYTES,
            subprotocols=(_SUBPROTOCOL,),
        )

        self._cursor: t.Optional[int] = None

        self._compression = ZstdDecompression(_MAX_MESSAGE_SIZE_BYTES) if compress else None
        self._dictionary_needs_refresh = compress
        self._rejected_dictionary_id: t.Optional[int] = None

    @property
    def cursor(self) -> t.Optional[int]:
        """:obj:`int`: Seq of the last delivered event, or :obj:`None` if nothing was delivered yet.

        Persist it to resume the stream later. Reconnects resume from it automatically.
        """
        return self._cursor

    @property
    def compressed(self) -> bool:
        """:obj:`bool`: Whether frames are being received compressed.

        Compression is best-effort: it degrades to an uncompressed stream rather than failing.
        """
        return self._compression is not None and self._compression.dictionary_id is not None

    @property
    def _http_origin(self) -> str:
        """HTTP origin of the same host, so the caller supplies it only once."""
        scheme, separator, rest = self._base_uri.partition('://')
        if not separator:
            return self._base_uri

        return f'{_WS_SCHEME_TO_HTTP.get(scheme, scheme)}://{rest}'

    def _set_param(self, name: str, value: t.Any) -> None:
        if self._params is None:
            self._params = {}

        self._params[name] = value

    def _track_cursor(self, seq: int) -> None:
        self._cursor = seq
        self._set_param('cursor', seq)

    def _use_dictionary(self, blob: bytes) -> None:
        """Adopt a freshly fetched dictionary, or shed compression if it is unusable."""
        if self._compression is None:
            return

        try:
            dictionary_id = self._compression.load(blob)
        except JetstreamDecodingError:
            self._shed_compression()
            return

        if dictionary_id == self._rejected_dictionary_id:
            # a mixed-version fleet keeps handing back the id that was just refused
            self._shed_compression()
            return

        self._dictionary_needs_refresh = False
        self._set_param(_ZSTD_DICTIONARY_PARAM, dictionary_id)

    def _shed_compression(self) -> None:
        """Give up on compression for the client's lifetime. The tail must keep flowing."""
        self._compression = None
        self._dictionary_needs_refresh = False
        if self._params is not None:
            self._params.pop(_ZSTD_DICTIONARY_PARAM, None)

    def _decode_frame(self, raw_frame: t.Union[str, bytes]) -> t.Optional[SubscribeEventsMessage]:
        if self._compression is not None and isinstance(raw_frame, (bytes, bytearray)):
            raw_frame = self._compression.decompress(bytes(raw_frame))

        frame = parse_frame(raw_frame)
        if isinstance(frame, ErrorFrame):
            raise _error_frame_to_exception(frame)

        message = parse_subscribe_events_message(t.cast('MessageFrame', frame))

        seq = getattr(message, 'seq', None)
        if seq is None:
            # #info advisories carry no seq and must not advance the cursor
            return message

        if self._cursor is not None and seq <= self._cursor:
            # the server replays inclusively, so every reconnect redelivers the last event
            return None

        self._track_cursor(seq)

        return message

    def _handle_frame_decoding_error(self, exception: Exception) -> None:
        if isinstance(exception, JetstreamDecodingError):
            # Ignore a frame that could not be decoded, including unknown types sent by
            # a newer server. Skipping one frame beats dropping the whole connection.
            return

        raise exception

    def _handle_websocket_error_or_stop(self, exception: Exception) -> bool:
        if isinstance(exception, JetstreamConsumerTooSlowError):
            return False

        if isinstance(exception, InvalidStatus):
            if self._is_dictionary_rejected(exception):
                return False

            fatal = _rejected_handshake_to_exception(exception)
            if fatal is not None:
                raise fatal from exception

        return super()._handle_websocket_error_or_stop(exception)

    def _is_dictionary_rejected(self, exception: InvalidStatus) -> bool:
        """Note a rotated dictionary so the next connect refetches it."""
        if self._compression is None:
            return False

        xrpc_error = _parse_xrpc_error(getattr(exception.response, 'body', None))
        if xrpc_error is None or xrpc_error.error != _UNKNOWN_ZSTD_DICTIONARY:
            return False

        self._rejected_dictionary_id = self._compression.dictionary_id
        self._compression.unload()
        self._dictionary_needs_refresh = True

        return True


class _JetstreamClient(_JetstreamClientMixin, WebsocketClient):
    """Jetstream subscription client."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._xrpc_client: t.Optional[ClientRaw] = None

    def _before_connect(self) -> None:
        if self._compression is None or not self._dictionary_needs_refresh:
            return

        if self._xrpc_client is None:
            self._xrpc_client = ClientRaw(base_url=self._http_origin)

        try:
            blob = self._xrpc_client.network.bsky.jetstream.get_zstd_dictionary()
        except Exception:  # noqa: BLE001
            self._shed_compression()
            return

        self._use_dictionary(blob)


class _AsyncJetstreamClient(_JetstreamClientMixin, AsyncWebsocketClient):
    """Async jetstream subscription client."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._xrpc_client: t.Optional[AsyncClientRaw] = None

    async def _before_connect(self) -> None:
        if self._compression is None or not self._dictionary_needs_refresh:
            return

        if self._xrpc_client is None:
            self._xrpc_client = AsyncClientRaw(base_url=self._http_origin)

        try:
            blob = await self._xrpc_client.network.bsky.jetstream.get_zstd_dictionary()
        except Exception:  # noqa: BLE001
            self._shed_compression()
            return

        self._use_dictionary(blob)
