import typing as t

from atproto.xrpc_client.client.base import ClientBase
from atproto.xrpc_client.namespaces import sync_ns

# TODO(MarshalX): This file should be autogenerated!


class ClientRaw(ClientBase):
    """Group all root namespaces"""

    com: 'sync_ns.ComNamespace'
    app: 'sync_ns.AppNamespace'

    def __init__(self, *args, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self.com = sync_ns.ComNamespace(self)
        self.app = sync_ns.AppNamespace(self)
