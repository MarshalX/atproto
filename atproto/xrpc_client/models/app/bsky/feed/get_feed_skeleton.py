##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getFeedSkeleton`."""

    feed: str  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, min_length=1, max_length=100)  #: Limit.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getFeedSkeleton`."""

    feed: t.List['models.AppBskyFeedDefs.SkeletonFeedPost']  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.
