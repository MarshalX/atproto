##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class PostView(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        uri: Uri.
        cid: Cid.
        author: Author.
        record: Record.
        embed: Embed.
        replyCount: Reply count.
        repostCount: Repost count.
        likeCount: Like count.
        indexedAt: Indexed at.
        viewer: Viewer.
        labels: Labels.
    """

    author: 'models.AppBskyActorDefs.ProfileViewBasic'
    cid: str
    indexedAt: str
    record: 'base.RecordModelBase'
    uri: str
    embed: Optional[
        Union[
            'models.AppBskyEmbedImages.View',
            'models.AppBskyEmbedExternal.View',
            'models.AppBskyEmbedRecord.View',
            'models.AppBskyEmbedRecordWithMedia.View',
            'Dict[str, Any]',
        ]
    ] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None
    likeCount: Optional[int] = None
    replyCount: Optional[int] = None
    repostCount: Optional[int] = None
    viewer: Optional['models.AppBskyFeedDefs.ViewerState'] = None


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        repost: Repost.
        like: Like.
    """

    like: Optional[str] = None
    repost: Optional[str] = None


@dataclass
class FeedViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        post: Post.
        reply: Reply.
        reason: Reason.
    """

    post: 'models.AppBskyFeedDefs.PostView'
    reason: Optional[Union['models.AppBskyFeedDefs.ReasonRepost', 'Dict[str, Any]']] = None
    reply: Optional['models.AppBskyFeedDefs.ReplyRef'] = None


@dataclass
class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        root: Root.
        parent: Parent.
    """

    parent: 'models.AppBskyFeedDefs.PostView'
    root: 'models.AppBskyFeedDefs.PostView'


@dataclass
class ReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        by: By.
        indexedAt: Indexed at.
    """

    by: 'models.AppBskyActorDefs.ProfileViewBasic'
    indexedAt: str


@dataclass
class ThreadViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        post: Post.
        parent: Parent.
        replies: Replies.
    """

    post: 'models.AppBskyFeedDefs.PostView'
    parent: Optional[
        Union[
            'models.AppBskyFeedDefs.ThreadViewPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
            'Dict[str, Any]',
        ]
    ] = None
    replies: Optional[
        List[
            Union[
                'models.AppBskyFeedDefs.ThreadViewPost',
                'models.AppBskyFeedDefs.NotFoundPost',
                'models.AppBskyFeedDefs.BlockedPost',
                'Dict[str, Any]',
            ]
        ]
    ] = None


@dataclass
class NotFoundPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        uri: Uri.
        notFound: Not found.
    """

    notFound: bool
    uri: str


@dataclass
class BlockedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        uri: Uri.
        blocked: Blocked.
    """

    blocked: bool
    uri: str
