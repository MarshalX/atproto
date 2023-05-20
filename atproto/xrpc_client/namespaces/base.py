import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from atproto.xrpc_client.client.async_raw import AsyncClientRaw
    from atproto.xrpc_client.client.raw import ClientRaw


@dataclass
class NamespaceBase:
    _client: t.Union['ClientRaw', 'AsyncClientRaw']


@dataclass
class DefaultNamespace:
    """placeholder"""
