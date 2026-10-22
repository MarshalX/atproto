import typing as t

from atproto_core.lazy_exports import lazy_exports

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.client.async_client import AsyncClient
    from atproto_client.client.client import Client
    from atproto_client.client.session import Session, SessionEvent

__all__ = [
    'AsyncClient',
    'Client',
    'Session',
    'SessionEvent',
    'models',
]

__getattr__, __dir__ = lazy_exports(
    __name__,
    attributes={
        'atproto_client.client.async_client': ('AsyncClient',),
        'atproto_client.client.client': ('Client',),
        'atproto_client.client.session': ('Session', 'SessionEvent'),
    },
)
