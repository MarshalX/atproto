#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.client.base import AsyncClientBase
from atproto_client.namespaces import async_ns


class AsyncClientRaw(AsyncClientBase):
    """Group all root namespaces."""

    app: 'async_ns.AppNamespace'
    chat: 'async_ns.ChatNamespace'
    com: 'async_ns.ComNamespace'
    internal: 'async_ns.InternalNamespace'
    network: 'async_ns.NetworkNamespace'
    site: 'async_ns.SiteNamespace'
    tools: 'async_ns.ToolsNamespace'

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self.app = async_ns.AppNamespace(self)
        self.chat = async_ns.ChatNamespace(self)
        self.com = async_ns.ComNamespace(self)
        self.internal = async_ns.InternalNamespace(self)
        self.network = async_ns.NetworkNamespace(self)
        self.site = async_ns.SiteNamespace(self)
        self.tools = async_ns.ToolsNamespace(self)
