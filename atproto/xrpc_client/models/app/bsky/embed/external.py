##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models import base


class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    external: 'models.AppBskyEmbedExternal.External'  #: External.

    py_type: te.Literal['app.bsky.embed.external'] = Field(
        default='app.bsky.embed.external', alias='$type', frozen=True
    )


class External(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: str  #: Uri.
    thumb: t.Optional['BlobRef'] = None  #: Thumb.

    py_type: te.Literal['app.bsky.embed.external#external'] = Field(
        default='app.bsky.embed.external#external', alias='$type', frozen=True
    )


class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    external: 'models.AppBskyEmbedExternal.ViewExternal'  #: External.

    py_type: te.Literal['app.bsky.embed.external#view'] = Field(
        default='app.bsky.embed.external#view', alias='$type', frozen=True
    )


class ViewExternal(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`."""

    description: str  #: Description.
    title: str  #: Title.
    uri: str  #: Uri.
    thumb: t.Optional[str] = None  #: Thumb.

    py_type: te.Literal['app.bsky.embed.external#viewExternal'] = Field(
        default='app.bsky.embed.external#viewExternal', alias='$type', frozen=True
    )
