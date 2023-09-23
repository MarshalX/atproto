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
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getPostThread`."""

    uri: str  #: Uri.
    depth: t.Optional[int] = Field(default=6, ge=0, le=1000)  #: Depth.
    parent_height: t.Optional[int] = Field(default=80, alias='parentHeight', ge=0, le=1000)  #: Parent height.


class ParamsDict(te.TypedDict):
    uri: str  #: Uri.
    depth: te.NotRequired[t.Optional[int]]  #: Depth.
    parent_height: te.NotRequired[t.Optional[int]]  #: Parent height.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getPostThread`."""

    thread: te.Annotated[
        t.Union[
            'models.AppBskyFeedDefs.ThreadViewPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
        ],
        Field(discriminator='py_type'),
    ]  #: Thread.
