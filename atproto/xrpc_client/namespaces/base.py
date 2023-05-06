from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from atproto.xrpc_client.client.async_raw import AsyncClientRaw
    from atproto.xrpc_client.client.raw import ClientRaw


@dataclass
class NamespaceBase:
    _client: Union['ClientRaw', 'AsyncClientRaw']


@dataclass
class DefaultNamespace:
    """placeholder"""
