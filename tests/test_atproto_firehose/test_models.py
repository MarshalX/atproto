"""Framing of decoded Firehose frames."""

import libipld
import pytest
from atproto_firehose.exceptions import FirehoseDecodingError
from atproto_firehose.models import (
    ErrorFrame,
    ErrorFrameHeader,
    Frame,
    FrameType,
    MessageFrame,
    MessageFrameHeader,
)

from .conftest import error_frame, message_frame


def test_message_frame_header() -> None:
    frame = Frame.from_bytes(message_frame(seq=1))

    assert isinstance(frame, MessageFrame)
    assert isinstance(frame.header, MessageFrameHeader)
    assert frame.header.op is FrameType.MESSAGE
    assert frame.operation is FrameType.MESSAGE
    assert frame.is_message
    assert not frame.is_error
    assert frame.type == '#commit'


def test_error_frame_header() -> None:
    frame = Frame.from_bytes(error_frame('ConsumerTooSlow', 'stream consumer too slow'))

    assert isinstance(frame, ErrorFrame)
    assert isinstance(frame.header, ErrorFrameHeader)
    assert frame.header.op is FrameType.ERROR
    assert frame.operation is FrameType.ERROR
    assert frame.is_error
    assert not frame.is_message
    assert frame.body.error == 'ConsumerTooSlow'
    assert frame.body.message == 'stream consumer too slow'


def test_unknown_operation_is_rejected() -> None:
    raw = libipld.encode_dag_cbor({'op': 42}) + libipld.encode_dag_cbor({})

    with pytest.raises(FirehoseDecodingError):
        Frame.from_bytes(raw)
