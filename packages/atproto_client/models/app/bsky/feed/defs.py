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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class PostView(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: str  #: Cid.
    indexed_at: str  #: Indexed at.
    record: 'UnknownType'  #: Record.
    uri: str  #: Uri.
    embed: t.Optional[
        te.Annotated[
            t.Union[
                'models.AppBskyEmbedImages.View',
                'models.AppBskyEmbedExternal.View',
                'models.AppBskyEmbedRecord.View',
                'models.AppBskyEmbedRecordWithMedia.View',
            ],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Embed.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: t.Optional[int] = None  #: Like count.
    reply_count: t.Optional[int] = None  #: Reply count.
    repost_count: t.Optional[int] = None  #: Repost count.
    threadgate: t.Optional['models.AppBskyFeedDefs.ThreadgateView'] = None  #: Threadgate.
    viewer: t.Optional['models.AppBskyFeedDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.feed.defs#postView'] = Field(
        default='app.bsky.feed.defs#postView', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`. Metadata about the requesting account's relationship with the subject content. Only has meaningful content for authed requests."""

    like: t.Optional[str] = None  #: Like.
    reply_disabled: t.Optional[bool] = None  #: Reply disabled.
    repost: t.Optional[str] = None  #: Repost.

    py_type: t.Literal['app.bsky.feed.defs#viewerState'] = Field(
        default='app.bsky.feed.defs#viewerState', alias='$type', frozen=True
    )


class FeedViewPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: 'models.AppBskyFeedDefs.PostView'  #: Post.
    feed_context: t.Optional[str] = Field(
        default=None, max_length=2000
    )  #: Context provided by feed generator that may be passed back alongside interactions.
    reason: t.Optional[
        te.Annotated[t.Union['models.AppBskyFeedDefs.ReasonRepost'], Field(default=None, discriminator='py_type')]
    ] = None  #: Reason.
    reply: t.Optional['models.AppBskyFeedDefs.ReplyRef'] = None  #: Reply.

    py_type: t.Literal['app.bsky.feed.defs#feedViewPost'] = Field(
        default='app.bsky.feed.defs#feedViewPost', alias='$type', frozen=True
    )


class ReplyRef(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    parent: te.Annotated[
        t.Union[
            'models.AppBskyFeedDefs.PostView',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
        ],
        Field(discriminator='py_type'),
    ]  #: Parent.
    root: te.Annotated[
        t.Union[
            'models.AppBskyFeedDefs.PostView',
            'models.AppBskyFeedDefs.NotFoundPost',
            'models.AppBskyFeedDefs.BlockedPost',
        ],
        Field(discriminator='py_type'),
    ]  #: Root.
    grandparent_author: t.Optional[
        'models.AppBskyActorDefs.ProfileViewBasic'
    ] = None  #: When parent is a reply to another post, this is the author of that post.

    py_type: t.Literal['app.bsky.feed.defs#replyRef'] = Field(
        default='app.bsky.feed.defs#replyRef', alias='$type', frozen=True
    )


class ReasonRepost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    by: 'models.AppBskyActorDefs.ProfileViewBasic'  #: By.
    indexed_at: str  #: Indexed at.

    py_type: t.Literal['app.bsky.feed.defs#reasonRepost'] = Field(
        default='app.bsky.feed.defs#reasonRepost', alias='$type', frozen=True
    )


class ThreadViewPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: 'models.AppBskyFeedDefs.PostView'  #: Post.
    parent: t.Optional[
        te.Annotated[
            t.Union[
                'models.AppBskyFeedDefs.ThreadViewPost',
                'models.AppBskyFeedDefs.NotFoundPost',
                'models.AppBskyFeedDefs.BlockedPost',
            ],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Parent.
    replies: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.AppBskyFeedDefs.ThreadViewPost',
                    'models.AppBskyFeedDefs.NotFoundPost',
                    'models.AppBskyFeedDefs.BlockedPost',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = None  #: Replies.

    py_type: t.Literal['app.bsky.feed.defs#threadViewPost'] = Field(
        default='app.bsky.feed.defs#threadViewPost', alias='$type', frozen=True
    )


class NotFoundPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    not_found: bool = Field(frozen=True)  #: Not found.
    uri: str  #: Uri.

    py_type: t.Literal['app.bsky.feed.defs#notFoundPost'] = Field(
        default='app.bsky.feed.defs#notFoundPost', alias='$type', frozen=True
    )


class BlockedPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    author: 'models.AppBskyFeedDefs.BlockedAuthor'  #: Author.
    blocked: bool = Field(frozen=True)  #: Blocked.
    uri: str  #: Uri.

    py_type: t.Literal['app.bsky.feed.defs#blockedPost'] = Field(
        default='app.bsky.feed.defs#blockedPost', alias='$type', frozen=True
    )


class BlockedAuthor(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    did: str  #: Did.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.feed.defs#blockedAuthor'] = Field(
        default='app.bsky.feed.defs#blockedAuthor', alias='$type', frozen=True
    )


class GeneratorView(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    did: str  #: Did.
    display_name: str  #: Display name.
    indexed_at: str  #: Indexed at.
    uri: str  #: Uri.
    accepts_interactions: t.Optional[bool] = None  #: Accepts interactions.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    like_count: t.Optional[int] = Field(default=None, ge=0)  #: Like count.
    viewer: t.Optional['models.AppBskyFeedDefs.GeneratorViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.feed.defs#generatorView'] = Field(
        default='app.bsky.feed.defs#generatorView', alias='$type', frozen=True
    )


class GeneratorViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    like: t.Optional[str] = None  #: Like.

    py_type: t.Literal['app.bsky.feed.defs#generatorViewerState'] = Field(
        default='app.bsky.feed.defs#generatorViewerState', alias='$type', frozen=True
    )


class SkeletonFeedPost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: str  #: Post.
    feed_context: t.Optional[str] = Field(
        default=None, max_length=2000
    )  #: Context that will be passed through to client and may be passed to feed generator back alongside interactions.
    reason: t.Optional[
        te.Annotated[
            t.Union['models.AppBskyFeedDefs.SkeletonReasonRepost'], Field(default=None, discriminator='py_type')
        ]
    ] = None  #: Reason.

    py_type: t.Literal['app.bsky.feed.defs#skeletonFeedPost'] = Field(
        default='app.bsky.feed.defs#skeletonFeedPost', alias='$type', frozen=True
    )


class SkeletonReasonRepost(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    repost: str  #: Repost.

    py_type: t.Literal['app.bsky.feed.defs#skeletonReasonRepost'] = Field(
        default='app.bsky.feed.defs#skeletonReasonRepost', alias='$type', frozen=True
    )


class ThreadgateView(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    cid: t.Optional[str] = None  #: Cid.
    lists: t.Optional[t.List['models.AppBskyGraphDefs.ListViewBasic']] = None  #: Lists.
    record: t.Optional['UnknownType'] = None  #: Record.
    uri: t.Optional[str] = None  #: Uri.

    py_type: t.Literal['app.bsky.feed.defs#threadgateView'] = Field(
        default='app.bsky.feed.defs#threadgateView', alias='$type', frozen=True
    )


class Interaction(base.ModelBase):
    """Definition model for :obj:`app.bsky.feed.defs`."""

    event: t.Optional[str] = None  #: Event.
    feed_context: t.Optional[str] = Field(
        default=None, max_length=2000
    )  #: Context on a feed item that was orginally supplied by the feed generator on getFeedSkeleton.
    item: t.Optional[str] = None  #: Item.

    py_type: t.Literal['app.bsky.feed.defs#interaction'] = Field(
        default='app.bsky.feed.defs#interaction', alias='$type', frozen=True
    )


RequestLess = t.Literal[
    'app.bsky.feed.defs#requestLess'
]  #: Request that less content like the given feed item be shown in the feed

RequestMore = t.Literal[
    'app.bsky.feed.defs#requestMore'
]  #: Request that more content like the given feed item be shown in the feed

ClickthroughItem = t.Literal['app.bsky.feed.defs#clickthroughItem']  #: User clicked through to the feed item

ClickthroughAuthor = t.Literal[
    'app.bsky.feed.defs#clickthroughAuthor'
]  #: User clicked through to the author of the feed item

ClickthroughReposter = t.Literal[
    'app.bsky.feed.defs#clickthroughReposter'
]  #: User clicked through to the reposter of the feed item

ClickthroughEmbed = t.Literal[
    'app.bsky.feed.defs#clickthroughEmbed'
]  #: User clicked through to the embedded content of the feed item

InteractionSeen = t.Literal['app.bsky.feed.defs#interactionSeen']  #: Feed item was seen by user

InteractionLike = t.Literal['app.bsky.feed.defs#interactionLike']  #: User liked the feed item

InteractionRepost = t.Literal['app.bsky.feed.defs#interactionRepost']  #: User reposted the feed item

InteractionReply = t.Literal['app.bsky.feed.defs#interactionReply']  #: User replied to the feed item

InteractionQuote = t.Literal['app.bsky.feed.defs#interactionQuote']  #: User quoted the feed item

InteractionShare = t.Literal['app.bsky.feed.defs#interactionShare']  #: User shared the feed item
