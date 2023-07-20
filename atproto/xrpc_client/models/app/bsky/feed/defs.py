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

    """Definition model for :obj:`app.bsky.feed.defs`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    record: 'base.UnknownDict'  #: Record.
    uri: str  #: Uri.
    embed: t.Optional[
        t.Union[
            'models.AppBskyEmbedImages.View',
            'models.AppBskyEmbedExternal.View',
            'models.AppBskyEmbedRecord.View',
            'models.AppBskyEmbedRecordWithMedia.View',
            't.Dict[str, t.Any]',
        ]
    ] = None  #: Embed.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    likeCount: t.Optional[int] = None  #: Like count.
    replyCount: t.Optional[int] = None  #: Reply count.
    repostCount: t.Optional[int] = None  #: Repost count.
    viewer: t.Optional['models.AppBskyFeedDefs.ViewerState'] = None  #: Viewer.

    _type: str = 'app.bsky.feed.defs#postView'


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    like: t.Optional[str] = None  #: Like.
    repost: t.Optional[str] = None  #: Repost.

    _type: str = 'app.bsky.feed.defs#viewerState'


@dataclass
class FeedViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: 'models.AppBskyFeedDefs.PostView'  #: Post.
    reason: t.Optional[t.Union['models.AppBskyFeedDefs.ReasonRepost', 't.Dict[str, t.Any]']] = None  #: Reason.
    reply: t.Optional['models.AppBskyFeedDefs.ReplyRef'] = None  #: Reply.

    _type: str = 'app.bsky.feed.defs#feedViewPost'


@dataclass
class ReplyRef(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    parent: t.Union[
        'models.AppBskyFeedDefs.PostView',
        'models.AppBskyFeedDefs.NotFoundPost',
        'models.AppBskyFeedDefs.BlockedPost',
        't.Dict[str, t.Any]',
    ]  #: Parent.
    root: t.Union[
        'models.AppBskyFeedDefs.PostView',
        'models.AppBskyFeedDefs.NotFoundPost',
        'models.AppBskyFeedDefs.BlockedPost',
        't.Dict[str, t.Any]',
    ]  #: Root.

    _type: str = 'app.bsky.feed.defs#replyRef'


@dataclass
class ReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    by: 'models.AppBskyActorDefs.ProfileViewBasic'  #: By.
    indexedAt: str  #: Indexed at.

    _type: str = 'app.bsky.feed.defs#reasonRepost'


@dataclass
class ThreadViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: 'models.AppBskyFeedDefs.PostView'  #: Post.
    parent: t.Optional[
        t.Union[
            'models.AppBskyFeedDefs.ThreadViewPost',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
            't.Dict[str, t.Any]',
        ]
    ] = None  #: Parent.
    replies: t.Optional[
        t.List[
            t.Union[
                'models.AppBskyFeedDefs.ThreadViewPost',
                'models.AppBskyFeedDefs.NotFoundPost',
                'models.AppBskyFeedDefs.BlockedPost',
                't.Dict[str, t.Any]',
            ]
        ]
    ] = None  #: Replies.

    _type: str = 'app.bsky.feed.defs#threadViewPost'


@dataclass
class NotFoundPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    notFound: bool  #: Not found.
    uri: str  #: Uri.

    _type: str = 'app.bsky.feed.defs#notFoundPost'


@dataclass
class BlockedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    blocked: bool  #: Blocked.
    uri: str  #: Uri.

    _type: str = 'app.bsky.feed.defs#blockedPost'


@dataclass
class GeneratorView(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    did: str  #: Did.
    displayName: str  #: Display name.
    indexedAt: str  #: Indexed at.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = None  #: Description.
    descriptionFacets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    likeCount: t.Optional[int] = None  #: Like count.
    viewer: t.Optional['models.AppBskyFeedDefs.GeneratorViewerState'] = None  #: Viewer.

    _type: str = 'app.bsky.feed.defs#generatorView'


@dataclass
class GeneratorViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    like: t.Optional[str] = None  #: Like.

    _type: str = 'app.bsky.feed.defs#generatorViewerState'


@dataclass
class SkeletonFeedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: str  #: Post.
    reason: t.Optional[t.Union['models.AppBskyFeedDefs.SkeletonReasonRepost', 't.Dict[str, t.Any]']] = None  #: Reason.

    _type: str = 'app.bsky.feed.defs#skeletonFeedPost'


@dataclass
class SkeletonReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    repost: str  #: Repost.

    _type: str = 'app.bsky.feed.defs#skeletonReasonRepost'
