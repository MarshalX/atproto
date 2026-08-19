#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Main(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.recordWithMedia`."""

    media: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyEmbedImages.Main',
            'models.AppBskyEmbedVideo.Main',
            'models.AppBskyEmbedGallery.Main',
            'models.AppBskyEmbedExternal.Main',
        ]
    ]  #: Media.
    record: 'models.AppBskyEmbedRecord.Main'  #: Record.

    py_type: t.Literal['app.bsky.embed.recordWithMedia'] = Field(
        default='app.bsky.embed.recordWithMedia', alias='$type', frozen=True
    )


class View(base.ModelBase):
    """Definition model for :obj:`app.bsky.embed.recordWithMedia`."""

    media: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyEmbedImages.View',
            'models.AppBskyEmbedVideo.View',
            'models.AppBskyEmbedGallery.View',
            'models.AppBskyEmbedExternal.View',
        ]
    ]  #: Media.
    record: 'models.AppBskyEmbedRecord.View'  #: Record.

    py_type: t.Literal['app.bsky.embed.recordWithMedia#view'] = Field(
        default='app.bsky.embed.recordWithMedia#view', alias='$type', frozen=True
    )
