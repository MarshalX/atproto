#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Bookmark(base.ModelBase):
    """Definition model for :obj:`app.bsky.bookmark.defs`. Object used to store bookmark data in stash."""

    subject: 'models.ComAtprotoRepoStrongRef.Main'  #: A strong ref to the record to be bookmarked. Currently, only `app.bsky.feed.post` records are supported.

    py_type: t.Literal['app.bsky.bookmark.defs#bookmark'] = Field(
        default='app.bsky.bookmark.defs#bookmark', alias='$type', frozen=True
    )


class BookmarkView(base.ModelBase):
    """Definition model for :obj:`app.bsky.bookmark.defs`."""

    item: unknown_union.OpenUnion[
        t.Union[
            'models.AppBskyFeedDefs.BlockedPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.PostView',
        ]
    ]  #: Item.
    subject: 'models.ComAtprotoRepoStrongRef.Main'  #: A strong ref to the bookmarked record.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.

    py_type: t.Literal['app.bsky.bookmark.defs#bookmarkView'] = Field(
        default='app.bsky.bookmark.defs#bookmarkView', alias='$type', frozen=True
    )
