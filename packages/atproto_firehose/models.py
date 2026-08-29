"""Moved to :mod:`atproto_subscription.frames`.

.. deprecated::
    Import from :mod:`atproto_subscription` instead.
"""

import importlib
import typing as t
import warnings

if t.TYPE_CHECKING:
    from atproto_subscription.frames import (
        ErrorFrame,
        ErrorFrameBody,
        ErrorFrameHeader,
        Frame,
        FrameHeader,
        FrameType,
        MessageFrame,
        MessageFrameHeader,
        parse_frame,
        parse_frame_header,
    )

_TARGET = 'atproto_subscription.frames'
_MOVED = (
    'ErrorFrame',
    'ErrorFrameBody',
    'ErrorFrameHeader',
    'Frame',
    'FrameHeader',
    'FrameType',
    'MessageFrame',
    'MessageFrameHeader',
    'parse_frame',
    'parse_frame_header',
)

__all__ = [
    'ErrorFrame',
    'ErrorFrameBody',
    'ErrorFrameHeader',
    'Frame',
    'FrameHeader',
    'FrameType',
    'MessageFrame',
    'MessageFrameHeader',
    'parse_frame',
    'parse_frame_header',
]


def __getattr__(name: str) -> t.Any:
    if name not in _MOVED:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

    warnings.warn(f'`{__name__}.{name}` moved to `{_TARGET}.{name}`.', DeprecationWarning, stacklevel=2)

    return getattr(importlib.import_module(_TARGET), name)
