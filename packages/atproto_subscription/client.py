import typing as t

from atproto_client.models import get_model_as_dict
from atproto_client.models.base import ParamsModelBase
from atproto_client.models.common import XrpcError
from atproto_core.exceptions import DAGCBORDecodingError

from atproto_subscription.exceptions import FrameDecodingError, SubscriptionError
from atproto_subscription.frames import ErrorFrame, Frame, MessageFrame
from atproto_subscription.websocket import AsyncWebsocketClient, WebsocketClient, WebsocketClientBase

_MAX_MESSAGE_SIZE_BYTES = 1024 * 1024 * 5  # 5MB

OnMessageCallback = t.Callable[['MessageFrame'], None]
AsyncOnMessageCallback = t.Callable[['MessageFrame'], t.Coroutine[t.Any, t.Any, None]]

OnCallbackErrorCallback = t.Callable[[BaseException], None]
AsyncOnCallbackErrorCallback = t.Callable[[BaseException], t.Coroutine[t.Any, t.Any, None]]


def _get_message_frame_from_bytes_or_raise(data: bytes) -> MessageFrame:
    frame = Frame.from_bytes(data)
    if isinstance(frame, ErrorFrame):
        raise SubscriptionError(XrpcError(frame.body.error, frame.body.message))
    if isinstance(frame, MessageFrame):
        return frame
    raise FrameDecodingError('Unknown frame type')


class _SubscriptionClientMixin(WebsocketClientBase):
    """Firehose framing on top of the shared websocket client."""

    _error_class = SubscriptionError

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
            params,
            recv_timeout,
            max_message_size_bytes=_MAX_MESSAGE_SIZE_BYTES,
        )

    def update_params(self, params: t.Union[ParamsModelBase, t.Dict[str, t.Any]]) -> None:
        """Update params.

        Warning:
            If you are using `params` arg at the client start, you must care about keeping params up to date.
            Otherwise, your client will be rolled back to the previous state (cursor) on reconnecting.
        """
        if isinstance(params, ParamsModelBase):
            params = get_model_as_dict(params)

        super().update_params(params)

    def _decode_frame(self, raw_frame: t.Union[str, bytes]) -> t.Optional[MessageFrame]:
        if isinstance(raw_frame, str):
            # skip text frames (should not be occurred)
            return None

        return _get_message_frame_from_bytes_or_raise(raw_frame)

    def _handle_frame_decoding_error(self, exception: Exception) -> None:
        if isinstance(exception, (DAGCBORDecodingError, FrameDecodingError)):
            # Ignore an invalid atproto_firehose frame that could not be properly decoded.
            # It's better to ignore one frame rather than stop the whole connection
            # or trap into an infinite loop of reconnections.
            return

        raise exception


class _WebsocketClient(_SubscriptionClientMixin, WebsocketClient):
    """Firehose subscription client."""


class _AsyncWebsocketClient(_SubscriptionClientMixin, AsyncWebsocketClient):
    """Async firehose subscription client."""


SubscriptionClient = _WebsocketClient
AsyncSubscriptionClient = _AsyncWebsocketClient
