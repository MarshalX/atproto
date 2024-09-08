##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class Main(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.video`."""

    video: 'BlobRef'  #: Video.
    alt: t.Optional[str] = Field(
        default=None, max_length=10000
    )  #: Alt text description of the video, for accessibility.
    aspect_ratio: t.Optional['models.AppBskyEmbedDefs.AspectRatio'] = None  #: Aspect ratio.
    captions: t.Optional[t.List['models.AppBskyEmbedVideo.Caption']] = Field(default=None, max_length=20)  #: Captions.

    py_type: t.Literal['app.bsky.embed.video'] = Field(default='app.bsky.embed.video', alias='$type', frozen=True)


class Caption(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.video`."""

    file: 'BlobRef'  #: File.
    lang: str  #: Lang.

    py_type: t.Literal['app.bsky.embed.video#caption'] = Field(
        default='app.bsky.embed.video#caption', alias='$type', frozen=True
    )


class View(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.video`."""

    cid: str  #: Cid.
    playlist: str  #: Playlist.
    alt: t.Optional[str] = Field(default=None, max_length=10000)  #: Alt.
    aspect_ratio: t.Optional['models.AppBskyEmbedDefs.AspectRatio'] = None  #: Aspect ratio.
    thumbnail: t.Optional[str] = None  #: Thumbnail.

    py_type: t.Literal['app.bsky.embed.video#view'] = Field(
        default='app.bsky.embed.video#view', alias='$type', frozen=True
    )
