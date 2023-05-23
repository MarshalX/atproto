##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.recordWithMedia`."""

    media: t.Union[
        'models.AppBskyEmbedImages.Main', 'models.AppBskyEmbedExternal.Main', 't.Dict[str, t.Any]'
    ]  #: Media.
    record: 'models.AppBskyEmbedRecord.Main'  #: Record.

    _type: str = 'app.bsky.embed.recordWithMedia'


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.recordWithMedia`."""

    media: t.Union[
        'models.AppBskyEmbedImages.View', 'models.AppBskyEmbedExternal.View', 't.Dict[str, t.Any]'
    ]  #: Media.
    record: 'models.AppBskyEmbedRecord.View'  #: Record.

    _type: str = 'app.bsky.embed.recordWithMedia#view'
