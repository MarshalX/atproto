"""Moved to :mod:`atproto_subscription.client`.

.. deprecated::
    Use :obj:`atproto_subscription.SubscriptionClient` and
    :obj:`atproto_subscription.AsyncSubscriptionClient` instead.
"""

import importlib
import typing as t
import warnings

if t.TYPE_CHECKING:
    from atproto_subscription.client import AsyncSubscriptionClient as AsyncFirehoseClient
    from atproto_subscription.client import SubscriptionClient as FirehoseClient

_TARGET = 'atproto_subscription.client'
_MOVED = {'FirehoseClient': 'SubscriptionClient', 'AsyncFirehoseClient': 'AsyncSubscriptionClient'}

__all__ = ['AsyncFirehoseClient', 'FirehoseClient']


def __getattr__(name: str) -> t.Any:
    renamed = _MOVED.get(name)
    if renamed is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

    warnings.warn(f'`{__name__}.{name}` moved to `{_TARGET}.{renamed}`.', DeprecationWarning, stacklevel=2)

    return getattr(importlib.import_module(_TARGET), renamed)
