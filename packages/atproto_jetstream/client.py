import typing as t
from copy import deepcopy

from atproto_client.models.common import XrpcError
from atproto_core.websocket import AsyncWebsocketClient, WebsocketClient, WebsocketClientBase
from pydantic_core import from_json
from websockets.exceptions import InvalidStatus

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

    @property
    def cursor(self) -> t.Optional[int]:
        """:obj:`int`: Seq of the last delivered event, or :obj:`None` if nothing was delivered yet.

        Persist it to resume the stream later. Reconnects resume from it automatically.
        """
        return self._cursor

    def _track_cursor(self, seq: int) -> None:
        self._cursor = seq
        if self._params is None:
            self._params = {}

        self._params['cursor'] = seq

    def _decode_frame(self, raw_frame: t.Union[str, bytes]) -> t.Optional[SubscribeEventsMessage]:
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
            fatal = _rejected_handshake_to_exception(exception)
            if fatal is not None:
                raise fatal from exception

        return super()._handle_websocket_error_or_stop(exception)


class _JetstreamClient(_JetstreamClientMixin, WebsocketClient):
    """Jetstream subscription client."""


class _AsyncJetstreamClient(_JetstreamClientMixin, AsyncWebsocketClient):
    """Async jetstream subscription client."""
