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
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class PostView(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: str  #: Cid.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
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
    like_count: t.Optional[int] = Field(default=None, alias='likeCount')  #: Like count.
    reply_count: t.Optional[int] = Field(default=None, alias='replyCount')  #: Reply count.
    repost_count: t.Optional[int] = Field(default=None, alias='repostCount')  #: Repost count.
    threadgate: t.Optional['models.AppBskyFeedDefs.ThreadgateView'] = None  #: Threadgate.
    viewer: t.Optional['models.AppBskyFeedDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.feed.defs#postView'] = Field(
        default='app.bsky.feed.defs#postView', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    like: t.Optional[str] = None  #: Like.
    reply_disabled: t.Optional[bool] = Field(default=None, alias='replyDisabled')  #: Reply disabled.
    repost: t.Optional[str] = None  #: Repost.

    py_type: te.Literal['app.bsky.feed.defs#viewerState'] = Field(
        default='app.bsky.feed.defs#viewerState', alias='$type', frozen=True
    )


class FeedViewPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: 'models.AppBskyFeedDefs.PostView'  #: Post.
    reason: t.Optional[
        te.Annotated[t.Union['models.AppBskyFeedDefs.ReasonRepost'], Field(default=None, discriminator='py_type')]
    ] = None  #: Reason.
    reply: t.Optional['models.AppBskyFeedDefs.ReplyRef'] = None  #: Reply.

    py_type: te.Literal['app.bsky.feed.defs#feedViewPost'] = Field(
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

    py_type: te.Literal['app.bsky.feed.defs#replyRef'] = Field(
        default='app.bsky.feed.defs#replyRef', alias='$type', frozen=True
    )


class ReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    by: 'models.AppBskyActorDefs.ProfileViewBasic'  #: By.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.

    py_type: te.Literal['app.bsky.feed.defs#reasonRepost'] = Field(
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

    py_type: te.Literal['app.bsky.feed.defs#threadViewPost'] = Field(
        default='app.bsky.feed.defs#threadViewPost', alias='$type', frozen=True
    )


class NotFoundPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    not_found: bool = Field(alias='notFound', frozen=True)  #: Not found.
    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.feed.defs#notFoundPost'] = Field(
        default='app.bsky.feed.defs#notFoundPost', alias='$type', frozen=True
    )


class BlockedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    author: 'models.AppBskyFeedDefs.BlockedAuthor'  #: Author.
    blocked: bool = Field(frozen=True)  #: Blocked.
    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.feed.defs#blockedPost'] = Field(
        default='app.bsky.feed.defs#blockedPost', alias='$type', frozen=True
    )


class BlockedAuthor(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    did: str  #: Did.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.feed.defs#blockedAuthor'] = Field(
        default='app.bsky.feed.defs#blockedAuthor', alias='$type', frozen=True
    )


class GeneratorView(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    did: str  #: Did.
    display_name: str = Field(alias='displayName')  #: Display name.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = Field(
        default=None, alias='descriptionFacets'
    )  #: Description facets.
    like_count: t.Optional[int] = Field(default=None, alias='likeCount', ge=0)  #: Like count.
    viewer: t.Optional['models.AppBskyFeedDefs.GeneratorViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.feed.defs#generatorView'] = Field(
        default='app.bsky.feed.defs#generatorView', alias='$type', frozen=True
    )


class GeneratorViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    like: t.Optional[str] = None  #: Like.

    py_type: te.Literal['app.bsky.feed.defs#generatorViewerState'] = Field(
        default='app.bsky.feed.defs#generatorViewerState', alias='$type', frozen=True
    )


class SkeletonFeedPost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    post: str  #: Post.
    reason: t.Optional[
        te.Annotated[
            t.Union['models.AppBskyFeedDefs.SkeletonReasonRepost'], Field(default=None, discriminator='py_type')
        ]
    ] = None  #: Reason.

    py_type: te.Literal['app.bsky.feed.defs#skeletonFeedPost'] = Field(
        default='app.bsky.feed.defs#skeletonFeedPost', alias='$type', frozen=True
    )


class SkeletonReasonRepost(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    repost: str  #: Repost.

    py_type: te.Literal['app.bsky.feed.defs#skeletonReasonRepost'] = Field(
        default='app.bsky.feed.defs#skeletonReasonRepost', alias='$type', frozen=True
    )


class ThreadgateView(base.ModelBase):

    """Definition model for :obj:`app.bsky.feed.defs`."""

    cid: t.Optional[str] = None  #: Cid.
    lists: t.Optional[t.List['models.AppBskyGraphDefs.ListViewBasic']] = None  #: Lists.
    record: t.Optional['UnknownType'] = None  #: Record.
    uri: t.Optional[str] = None  #: Uri.

    py_type: te.Literal['app.bsky.feed.defs#threadgateView'] = Field(
        default='app.bsky.feed.defs#threadgateView', alias='$type', frozen=True
    )
