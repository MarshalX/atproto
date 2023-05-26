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
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getPostThread`."""

    uri: str  #: Uri.
    depth: t.Optional[int] = None  #: Depth.
    parentHeight: t.Optional[int] = None  #: Parent height.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getPostThread`."""

    thread: t.Union[
        'models.AppBskyFeedDefs.ThreadViewPost',
        'models.AppBskyFeedDefs.NotFoundPost',
        'models.AppBskyFeedDefs.BlockedPost',
        't.Dict[str, t.Any]',
    ]  #: Thread.
