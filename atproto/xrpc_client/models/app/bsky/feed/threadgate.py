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


class MentionRule(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors mentioned in your post."""

    py_type: te.Literal['app.bsky.feed.threadgate#mentionRule'] = Field(
        default='app.bsky.feed.threadgate#mentionRule', alias='$type', frozen=True
    )


class FollowingRule(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors you follow."""

    py_type: te.Literal['app.bsky.feed.threadgate#followingRule'] = Field(
        default='app.bsky.feed.threadgate#followingRule', alias='$type', frozen=True
    )


class ListRule(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.threadgate`. Allow replies from actors on a list."""

    list: str  #: List.

    py_type: te.Literal['app.bsky.feed.threadgate#listRule'] = Field(
        default='app.bsky.feed.threadgate#listRule', alias='$type', frozen=True
    )


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.threadgate`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    post: str  #: Post.
    allow: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.AppBskyFeedThreadgate.MentionRule',
                    'models.AppBskyFeedThreadgate.FollowingRule',
                    'models.AppBskyFeedThreadgate.ListRule',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = Field(default=None, max_length=5)  #: Allow.

    py_type: te.Literal['app.bsky.feed.threadgate'] = Field(
        default='app.bsky.feed.threadgate', alias='$type', frozen=True
    )
