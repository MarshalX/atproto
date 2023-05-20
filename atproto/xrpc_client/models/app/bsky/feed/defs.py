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
    embed: t.Optional[
        t.Union[
            'models.AppBskyEmbedImages.View',
            'models.AppBskyEmbedExternal.View',
            'models.AppBskyEmbedRecord.View',
            'models.AppBskyEmbedRecordWithMedia.View',
            't.Dict[str, t.Any]',
        ]
    ] = None
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None
    likeCount: t.Optional[int] = None
    replyCount: t.Optional[int] = None
    repostCount: t.Optional[int] = None
    viewer: t.Optional['models.AppBskyFeedDefs.ViewerState'] = None

    _type: str = 'app.bsky.feed.defs#postView'


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        repost: Repost.
        like: Like.
    """

    like: t.Optional[str] = None
    repost: t.Optional[str] = None

    _type: str = 'app.bsky.feed.defs#viewerState'


@dataclass
class FeedViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        post: Post.
        reply: Reply.
        reason: Reason.
    """

    post: 'models.AppBskyFeedDefs.PostView'
    reason: t.Optional[t.Union['models.AppBskyFeedDefs.ReasonRepost', 't.Dict[str, t.Any]']] = None
    reply: t.Optional['models.AppBskyFeedDefs.ReplyRef'] = None

    _type: str = 'app.bsky.feed.defs#feedViewPost'


@dataclass
class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        root: Root.
        parent: Parent.
    """

    parent: 'models.AppBskyFeedDefs.PostView'
    root: 'models.AppBskyFeedDefs.PostView'

    _type: str = 'app.bsky.feed.defs#replyRef'


@dataclass
class ReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        by: By.
        indexedAt: Indexed at.
    """

    by: 'models.AppBskyActorDefs.ProfileViewBasic'
    indexedAt: str

    _type: str = 'app.bsky.feed.defs#reasonRepost'


@dataclass
class ThreadViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        post: Post.
        parent: Parent.
        replies: Replies.
    """

    post: 'models.AppBskyFeedDefs.PostView'
    parent: t.Optional[
        t.Union[
            'models.AppBskyFeedDefs.ThreadViewPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
            't.Dict[str, t.Any]',
        ]
    ] = None
    replies: t.Optional[
        t.List[
            t.Union[
                'models.AppBskyFeedDefs.ThreadViewPost',
                'models.AppBskyFeedDefs.NotFoundPost',
                'models.AppBskyFeedDefs.BlockedPost',
                't.Dict[str, t.Any]',
            ]
        ]
    ] = None

    _type: str = 'app.bsky.feed.defs#threadViewPost'


@dataclass
class NotFoundPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        uri: Uri.
        notFound: Not found.
    """

    notFound: bool
    uri: str

    _type: str = 'app.bsky.feed.defs#notFoundPost'


@dataclass
class BlockedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`.

    Attributes:
        uri: Uri.
        blocked: Blocked.
    """

    blocked: bool
    uri: str

    _type: str = 'app.bsky.feed.defs#blockedPost'
