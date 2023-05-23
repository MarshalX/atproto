##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`."""

    images: t.List['models.AppBskyEmbedImages.Image']  #: Images.

    _type: str = 'app.bsky.embed.images'


@dataclass
class Image(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`."""

    alt: str  #: Alt.
    image: BlobRef  #: Image.

    _type: str = 'app.bsky.embed.images#image'


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`."""

    images: t.List['models.AppBskyEmbedImages.ViewImage']  #: Images.

    _type: str = 'app.bsky.embed.images#view'


@dataclass
class ViewImage(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`."""

    alt: str  #: Alt.
    fullsize: str  #: Fullsize.
    thumb: str  #: Thumb.

    _type: str = 'app.bsky.embed.images#viewImage'
