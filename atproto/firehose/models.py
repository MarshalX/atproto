from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from atproto.cbor import decode_multi
from atproto.exceptions import AtProtocolError, FirehoseError
from atproto.xrpc_client.models.utils import get_or_create_model


class FrameType(Enum):
    MESSAGE = 1
    ERROR = -1

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class MessageFrameHeader:
    op: FrameType = FrameType.MESSAGE
    t: Optional[str] = None


@dataclass
class ErrorFrameHeader:
    op: FrameType = FrameType.ERROR


FrameHeader = Union[MessageFrameHeader, ErrorFrameHeader]


@dataclass
class ErrorFrameBody:
    error: str
    message: Optional[str] = None


@dataclass
class Frame:
    header: Union[MessageFrameHeader, ErrorFrameHeader]
    body: Union[ErrorFrameBody, dict]

    @property
    def operation(self) -> FrameType:
        return self.header.op

    @property
    def type(self) -> str:
        return self.header.t

    @property
    def is_message(self) -> bool:
        return self.operation is FrameType.MESSAGE

    @property
    def is_error(self) -> bool:
        return self.operation is FrameType.ERROR

    @staticmethod
    def from_bytes(data: Union[bytes, bytearray]) -> Union['MessageFrame', 'ErrorFrame']:
        decoded_parts = decode_multi(data)
        if len(decoded_parts) > 2:
            raise FirehoseError('Too many CBOR data parts in the frame')
        if not len(decoded_parts):
            raise FirehoseError('Invalid frame without CBOR data')

        raw_header = decoded_parts[0]

        raw_body = None
        if len(decoded_parts) > 1:
            raw_body = decoded_parts[1]

        if raw_body is None:
            raise FirehoseError('Frame body not found')

        try:
            header_op = int(raw_header.get('op', 0))
            if header_op == FrameType.MESSAGE.value:
                header = get_or_create_model(raw_header, MessageFrameHeader)
            elif header_op == FrameType.ERROR.value:
                header = get_or_create_model(raw_header, ErrorFrameHeader)
            else:
                raise FirehoseError('Invalid frame type')
        except (ValueError, AtProtocolError):
            raise FirehoseError('Invalid frame header')

        try:
            if isinstance(header, ErrorFrameHeader):
                body = get_or_create_model(raw_body, ErrorFrameBody)
                return ErrorFrame(header, body)
            elif isinstance(header, MessageFrameHeader):
                return MessageFrame(header, raw_body)
            else:
                raise FirehoseError('Invalid frame type')
        except AtProtocolError:
            raise FirehoseError('Invalid frame body')


@dataclass
class MessageFrame(Frame):
    header: MessageFrameHeader
    body: dict

    @property
    def type(self) -> str:
        return self.header.t


@dataclass
class ErrorFrame(Frame):
    header: ErrorFrameHeader
    body: ErrorFrameBody
