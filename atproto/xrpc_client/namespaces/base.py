from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xrpc_client.test import ClientRaw


@dataclass
class NamespaceBase:
    _client: 'ClientRaw'


@dataclass
class DefaultNamespace:
    """placeholder"""
