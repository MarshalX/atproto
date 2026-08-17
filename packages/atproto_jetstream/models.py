import typing as t
from dataclasses import dataclass

from atproto_client import models
from atproto_client.models.utils import get_or_create
from pydantic_core import from_json

from atproto_jetstream.exceptions import JetstreamDecodingError

_MESSAGE_FRAME_TYPE = 'message'
_ERROR_FRAME_TYPE = 'error'

_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL = {
    'network.bsky.jetstream.subscribeEvents#commit': models.NetworkBskyJetstreamSubscribeEvents.Commit,
    'network.bsky.jetstream.subscribeEvents#identity': models.NetworkBskyJetstreamSubscribeEvents.Identity,
    'network.bsky.jetstream.subscribeEvents#account': models.NetworkBskyJetstreamSubscribeEvents.Account,
    'network.bsky.jetstream.subscribeEvents#sync': models.NetworkBskyJetstreamSubscribeEvents.Sync,
    'network.bsky.jetstream.subscribeEvents#info': models.NetworkBskyJetstreamSubscribeEvents.Info,
}

#: Subscribe Events Message
SubscribeEventsMessage = t.Union[
    models.NetworkBskyJetstreamSubscribeEvents.Commit,
    models.NetworkBskyJetstreamSubscribeEvents.Identity,
    models.NetworkBskyJetstreamSubscribeEvents.Account,
    models.NetworkBskyJetstreamSubscribeEvents.Sync,
    models.NetworkBskyJetstreamSubscribeEvents.Info,
]


@dataclass
class MessageFrame:
    """Jetstream message frame."""

    payload: dict  #: Payload.

    @property
    def type(self) -> t.Optional[str]:
        """:obj:`str`: Fully qualified type of the payload."""
        return self.payload.get('$type')


@dataclass
class ErrorFrame:
    """Jetstream error frame."""

    error: str  #: Code of the error.
    message: t.Optional[str] = None  #: Description of the error.


#: Base frame.
Frame = t.Union[MessageFrame, ErrorFrame]


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

    if not isinstance(raw_frame, dict):
        raise JetstreamDecodingError('Frame is not an object')

    frame_type = raw_frame.get('$type')
    if frame_type == _ERROR_FRAME_TYPE:
        return ErrorFrame(error=raw_frame.get('error', ''), message=raw_frame.get('message'))

    if frame_type == _MESSAGE_FRAME_TYPE:
        payload = raw_frame.get('payload')
        if not isinstance(payload, dict):
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

    return t.cast('SubscribeEventsMessage', get_or_create(message.payload, model_class))
