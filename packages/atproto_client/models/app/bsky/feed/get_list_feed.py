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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getListFeed`."""

    list: string_formats.AtUri  #: Reference (AT-URI) to the list record.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    since: t.Optional[str] = (
        None  #: Return only items newer than the position identified by this cursor value, newest first. Use the startCursor from a previous response. The item at that position is not returned because the caller already holds it. When the bounded range is exhausted, the returned cursor equals this value so that pagination continues below the boundary.
    )


class ParamsDict(t.TypedDict):
    list: string_formats.AtUri  #: Reference (AT-URI) to the list record.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    since: te.NotRequired[
        t.Optional[str]
    ]  #: Return only items newer than the position identified by this cursor value, newest first. Use the startCursor from a previous response. The item at that position is not returned because the caller already holds it. When the bounded range is exhausted, the returned cursor equals this value so that pagination continues below the boundary.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getListFeed`."""

    feed: t.List['models.AppBskyFeedDefs.FeedViewPost']  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.
    start_cursor: t.Optional[str] = (
        None  #: Cursor identifying the newest item in this page. Pass it as since on a later request to fetch only newer content.
    )
