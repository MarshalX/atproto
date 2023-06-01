import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from atproto.xrpc_client.client.async_raw import AsyncClientRaw
    from atproto.xrpc_client.client.raw import ClientRaw


class NamespaceBase:
    def __init__(self, client: 'ClientRaw') -> None:
        self._client: 'ClientRaw' = client


class AsyncNamespaceBase:
    def __init__(self, client: 'AsyncClientRaw') -> None:
        self._client: 'AsyncClientRaw' = client


@dataclass
class DefaultNamespace:
    """placeholder"""
