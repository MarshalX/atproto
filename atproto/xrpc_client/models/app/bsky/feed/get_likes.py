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

    """Parameters model for :obj:`app.bsky.feed.getLikes`.

    Attributes:
        uri: Uri.
        cid: Cid.
        limit: Limit.
        cursor: Cursor.
    """

    uri: str
    cid: t.Optional[str] = None
    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getLikes`.

    Attributes:
        uri: Uri.
        cid: Cid.
        cursor: Cursor.
        likes: Likes.
    """

    likes: t.List['models.AppBskyFeedGetLikes.Like']
    uri: str
    cid: t.Optional[str] = None
    cursor: t.Optional[str] = None


@dataclass
class Like(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.getLikes`.

    Attributes:
        indexedAt: Indexed at.
        createdAt: Created at.
        actor: Actor.
    """

    actor: 'models.AppBskyActorDefs.ProfileView'
    createdAt: str
    indexedAt: str

    _type: str = 'app.bsky.feed.getLikes#like'
