##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getAuthorFeed`."""

    actor: str  #: Actor.
    cursor: t.Optional[str] = None  #: Cursor.
    filter: t.Optional[
        t.Union[
            t.Literal['posts_with_replies'],
            t.Literal['posts_no_replies'],
            t.Literal['posts_with_media'],
            t.Literal['posts_and_author_threads'],
            str,
        ]
    ] = 'posts_with_replies'  #: Combinations of post/repost types to include in response.
    include_pins: t.Optional[bool] = False  #: Include pins.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.


class ParamsDict(t.TypedDict):
    actor: str  #: Actor.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    filter: te.NotRequired[
        t.Optional[
            t.Union[
                t.Literal['posts_with_replies'],
                t.Literal['posts_no_replies'],
                t.Literal['posts_with_media'],
                t.Literal['posts_and_author_threads'],
                str,
            ]
        ]
    ]  #: Combinations of post/repost types to include in response.
    include_pins: te.NotRequired[t.Optional[bool]]  #: Include pins.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getAuthorFeed`."""

    feed: t.List['models.AppBskyFeedDefs.FeedViewPost']  #: Feed.
    cursor: t.Optional[str] = None  #: Cursor.
