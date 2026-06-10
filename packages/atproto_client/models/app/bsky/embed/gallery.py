#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class Main(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.gallery`."""

    items: t.List[te.Annotated[t.Union['models.AppBskyEmbedGallery.Image'], Field(discriminator='py_type')]] = Field(
        max_length=20
    )  #: The schema-level maxLength of 20 is a future-proof ceiling. Clients should currently enforce a soft limit of 10 items in authoring UIs. The media items in the gallery. Each item may be of a different type, but all types must be supported by the client.

    py_type: t.Literal['app.bsky.embed.gallery'] = Field(default='app.bsky.embed.gallery', alias='$type', frozen=True)


class Image(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.gallery`."""

    alt: str  #: Alt text description of the image, for accessibility.
    aspect_ratio: 'models.AppBskyEmbedDefs.AspectRatio'  #: Aspect ratio.
    image: 'BlobRef'  #: Image.

    py_type: t.Literal['app.bsky.embed.gallery#image'] = Field(
        default='app.bsky.embed.gallery#image', alias='$type', frozen=True
    )


class View(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.gallery`."""

    items: t.List[
        te.Annotated[t.Union['models.AppBskyEmbedGallery.ViewImage'], Field(discriminator='py_type')]
    ]  #: Items.

    py_type: t.Literal['app.bsky.embed.gallery#view'] = Field(
        default='app.bsky.embed.gallery#view', alias='$type', frozen=True
    )


class ViewImage(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.gallery`."""

    alt: str  #: Alt text description of the image, for accessibility.
    aspect_ratio: 'models.AppBskyEmbedDefs.AspectRatio'  #: Aspect ratio.
    fullsize: string_formats.Uri  #: Fully-qualified URL where a large version of the image can be fetched. May or may not be the exact original blob. For example, CDN location provided by the App View.
    thumbnail: string_formats.Uri  #: Fully-qualified URL where a thumbnail of the image can be fetched. For example, CDN location provided by the App View.

    py_type: t.Literal['app.bsky.embed.gallery#viewImage'] = Field(
        default='app.bsky.embed.gallery#viewImage', alias='$type', frozen=True
    )
