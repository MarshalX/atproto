##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`.

    Attributes:
        images: Images.
    """

    images: List['models.AppBskyEmbedImages.Image']

    _type: str = 'app.bsky.embed.images'


@dataclass
class Image(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`.

    Attributes:
        image: Image.
        alt: Alt.
    """

    alt: str
    image: BlobRef


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`.

    Attributes:
        images: Images.
    """

    images: List['models.AppBskyEmbedImages.ViewImage']


@dataclass
class ViewImage(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.images`.

    Attributes:
        thumb: Thumb.
        fullsize: Fullsize.
        alt: Alt.
    """

    alt: str
    fullsize: str
    thumb: str
