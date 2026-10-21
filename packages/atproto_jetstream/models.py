import typing as t
from dataclasses import dataclass

import typing_extensions as te
from atproto_client.models.utils import get_or_create
from atproto_client.subscriptions import (
    NETWORK_BSKY_JETSTREAM_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL,
    NetworkBskyJetstreamSubscribeEventsMessage,
)
from pydantic_core import from_json

from atproto_jetstream.exceptions import JetstreamDecodingError

_MESSAGE_FRAME_TYPE = 'message'
_ERROR_FRAME_TYPE = 'error'

_NSID = 'network.bsky.jetstream.subscribeEvents'

# the generated map is keyed by fragment; Jetstream sends the fully qualified type
_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL = {
    f'{_NSID}{fragment}': model
    for fragment, model in NETWORK_BSKY_JETSTREAM_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL.items()
}

#: Subscribe Events Message
SubscribeEventsMessage = NetworkBskyJetstreamSubscribeEventsMessage


@dataclass
class MessageFrame:
    """Jetstream message frame."""

    payload: t.Dict[str, object]  #: Payload.

    @property
    def type(self) -> t.Optional[str]:
        """:obj:`str`: Fully qualified type of the payload."""
        payload_type = self.payload.get('$type')
        return payload_type if isinstance(payload_type, str) else None


@dataclass
class ErrorFrame:
    """Jetstream error frame."""

    error: str  #: Code of the error.
    message: t.Optional[str] = None  #: Description of the error.


#: Base frame.
Frame = t.Union[MessageFrame, ErrorFrame]


def _is_json_object(value: object) -> te.TypeGuard[t.Dict[str, object]]:
    return isinstance(value, dict)


def parse_frame(data: t.Union[str, bytes]) -> Frame:
    """Decode a frame of the `xrpc.v1.json` subprotocol.

    Args:
        data: Raw websocket frame.

    Returns:
        :obj:`atproto.jetstream_models.MessageFrame` or :obj:`atproto.jetstream_models.ErrorFrame`

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Invalid data frame.
    """
    try:
        raw_frame = from_json(data)
    except ValueError as e:
        raise JetstreamDecodingError('Invalid frame JSON') from e

    if not _is_json_object(raw_frame):
        raise JetstreamDecodingError('Frame is not an object')

    frame_type = raw_frame.get('$type')
    if frame_type == _ERROR_FRAME_TYPE:
        error = raw_frame.get('error', '')
        message = raw_frame.get('message')
        return ErrorFrame(
            error=error if isinstance(error, str) else '',
            message=message if isinstance(message, str) else None,
        )

    if frame_type == _MESSAGE_FRAME_TYPE:
        payload = raw_frame.get('payload')
        if not _is_json_object(payload):
            raise JetstreamDecodingError('Message frame without payload')

        return MessageFrame(payload=payload)

    raise JetstreamDecodingError(f'Unknown frame type: {frame_type}')


def parse_subscribe_events_message(message: MessageFrame) -> SubscribeEventsMessage:
    """Parse Jetstream message to the corresponding model.

    Args:
        message: Message frame.

    Returns:
        :obj:`SubscribeEventsMessage`: Corresponding message model.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Unknown message type.
    """
    model_class = _SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL.get(message.type or '')
    if model_class is None:
        raise JetstreamDecodingError(f'Unknown message type: {message.type}')

    return get_or_create(message.payload, model_class)
