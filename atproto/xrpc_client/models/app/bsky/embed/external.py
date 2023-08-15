##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models import base


class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    external: 'models.AppBskyEmbedExternal.External'  #: External.

    _type: str = 'app.bsky.embed.external'


class External(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: str  #: Uri.
    thumb: t.Optional['BlobRef'] = None  #: Thumb.

    _type: str = 'app.bsky.embed.external#external'


class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    external: 'models.AppBskyEmbedExternal.ViewExternal'  #: External.

    _type: str = 'app.bsky.embed.external#view'


class ViewExternal(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: str  #: Uri.
    thumb: t.Optional[str] = None  #: Thumb.

    _type: str = 'app.bsky.embed.external#viewExternal'
