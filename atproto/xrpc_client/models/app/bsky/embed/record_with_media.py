##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.recordWithMedia`.

    Attributes:
        record: Record.
        media: Media.
    """

    media: Union['models.AppBskyEmbedImages.Main', 'models.AppBskyEmbedExternal.Main', 'Dict[str, Any]']
    record: 'models.AppBskyEmbedRecord.Main'

    _type: str = 'app.bsky.embed.recordWithMedia'


@dataclass
class View(base.ModelBase):

    """Definition model for :obj:`app.bsky.embed.recordWithMedia`.

    Attributes:
        record: Record.
        media: Media.
    """

    media: Union['models.AppBskyEmbedImages.View', 'models.AppBskyEmbedExternal.View', 'Dict[str, Any]']
    record: 'models.AppBskyEmbedRecord.View'
