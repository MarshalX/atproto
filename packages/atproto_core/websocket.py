"""Moved to :mod:`atproto_subscription.websocket`.

.. deprecated::
    Import from :mod:`atproto_subscription` instead.
"""

import importlib
import typing as t
import warnings

if t.TYPE_CHECKING:
    from atproto_subscription.websocket import (
        AsyncWebsocketClient,
        WebsocketClient,
        WebsocketClientBase,
        build_websocket_uri,
    )

_TARGET = 'atproto_subscription.websocket'
_MOVED = ('AsyncWebsocketClient', 'WebsocketClient', 'WebsocketClientBase', 'build_websocket_uri')

__all__ = ['AsyncWebsocketClient', 'WebsocketClient', 'WebsocketClientBase', 'build_websocket_uri']


def __getattr__(name: str) -> t.Any:
    if name not in _MOVED:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

    warnings.warn(f'`{__name__}.{name}` moved to `{_TARGET}.{name}`.', DeprecationWarning, stacklevel=2)

    return getattr(importlib.import_module(_TARGET), name)
