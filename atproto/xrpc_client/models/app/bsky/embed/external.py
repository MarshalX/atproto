##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Optional

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`.

    Attributes:
        external: External.
    """

    external: 'models.AppBskyEmbedExternal.External'

    _type: str = 'app.bsky.embed.external'


@dataclass
class External(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`.

    Attributes:
        uri: Uri.
        title: Title.
        description: Description.
        thumb: Thumb.
    """

    description: str
    title: str
    uri: str
    thumb: Optional[BlobRef] = None


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`.

    Attributes:
        external: External.
    """

    external: 'models.AppBskyEmbedExternal.ViewExternal'


@dataclass
class ViewExternal(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.external`.

    Attributes:
        uri: Uri.
        title: Title.
        description: Description.
        thumb: Thumb.
    """

    description: str
    title: str
    uri: str
    thumb: Optional[str] = None
