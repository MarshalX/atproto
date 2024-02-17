##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getLikes`."""

    uri: str  #: AT-URI of the subject (eg, a post record).
    cid: t.Optional[str] = None  #: CID of the subject record (aka, specific version of record), to filter likes.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.


class ParamsDict(te.TypedDict):
    uri: str  #: AT-URI of the subject (eg, a post record).
    cid: te.NotRequired[
        t.Optional[str]
    ]  #: CID of the subject record (aka, specific version of record), to filter likes.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getLikes`."""

    likes: t.List['models.AppBskyFeedGetLikes.Like']  #: Likes.
    uri: str  #: Uri.
    cid: t.Optional[str] = None  #: Cid.
    cursor: t.Optional[str] = None  #: Cursor.


class Like(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.getLikes`."""

    actor: 'models.AppBskyActorDefs.ProfileView'  #: Actor.
    created_at: str  #: Created at.
    indexed_at: str  #: Indexed at.

    py_type: te.Literal['app.bsky.feed.getLikes#like'] = Field(
        default='app.bsky.feed.getLikes#like', alias='$type', frozen=True
    )
