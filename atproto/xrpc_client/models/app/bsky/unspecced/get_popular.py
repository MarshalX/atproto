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

    """Parameters model for :obj:`app.bsky.unspecced.getPopular`."""

    cursor: t.Optional[str] = None  #: Cursor.
    include_nsfw: t.Optional[bool] = Field(default=False, alias='includeNsfw')  #: Include nsfw.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    include_nsfw: te.NotRequired[t.Optional[bool]]  #: Include nsfw.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.unspecced.getPopular`."""

    feed: t.List['models.AppBskyFeedDefs.FeedViewPost']  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.
