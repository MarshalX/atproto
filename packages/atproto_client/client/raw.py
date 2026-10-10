#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.client.base import ClientBase
from atproto_client.namespaces import sync_ns


class ClientRaw(ClientBase):
    """Group all root namespaces."""

    app: 'sync_ns.AppNamespace'
    chat: 'sync_ns.ChatNamespace'
    com: 'sync_ns.ComNamespace'
    internal: 'sync_ns.InternalNamespace'
    network: 'sync_ns.NetworkNamespace'
    place: 'sync_ns.PlaceNamespace'
    site: 'sync_ns.SiteNamespace'
    social: 'sync_ns.SocialNamespace'
    tools: 'sync_ns.ToolsNamespace'

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self.app = sync_ns.AppNamespace(self)
        self.chat = sync_ns.ChatNamespace(self)
        self.com = sync_ns.ComNamespace(self)
        self.internal = sync_ns.InternalNamespace(self)
        self.network = sync_ns.NetworkNamespace(self)
        self.place = sync_ns.PlaceNamespace(self)
        self.site = sync_ns.SiteNamespace(self)
        self.social = sync_ns.SocialNamespace(self)
        self.tools = sync_ns.ToolsNamespace(self)
