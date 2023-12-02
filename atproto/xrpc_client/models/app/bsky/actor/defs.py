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


class ProfileViewBasic(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    display_name: t.Optional[str] = Field(default=None, alias='displayName', max_length=640)  #: Display name.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileViewBasic'] = Field(
        default='app.bsky.actor.defs#profileViewBasic', alias='$type', frozen=True
    )


class ProfileView(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, alias='displayName', max_length=640)  #: Display name.
    indexed_at: t.Optional[str] = Field(default=None, alias='indexedAt')  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileView'] = Field(
        default='app.bsky.actor.defs#profileView', alias='$type', frozen=True
    )


class ProfileViewDetailed(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    banner: t.Optional[str] = None  #: Banner.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, alias='displayName', max_length=640)  #: Display name.
    followers_count: t.Optional[int] = Field(default=None, alias='followersCount')  #: Followers count.
    follows_count: t.Optional[int] = Field(default=None, alias='followsCount')  #: Follows count.
    indexed_at: t.Optional[str] = Field(default=None, alias='indexedAt')  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    posts_count: t.Optional[int] = Field(default=None, alias='postsCount')  #: Posts count.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileViewDetailed'] = Field(
        default='app.bsky.actor.defs#profileViewDetailed', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    blocked_by: t.Optional[bool] = Field(default=None, alias='blockedBy')  #: Blocked by.
    blocking: t.Optional[str] = None  #: Blocking.
    blocking_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = Field(
        default=None, alias='blockingByList'
    )  #: Blocking by list.
    followed_by: t.Optional[str] = Field(default=None, alias='followedBy')  #: Followed by.
    following: t.Optional[str] = None  #: Following.
    muted: t.Optional[bool] = None  #: Muted.
    muted_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = Field(
        default=None, alias='mutedByList'
    )  #: Muted by list.

    py_type: te.Literal['app.bsky.actor.defs#viewerState'] = Field(
        default='app.bsky.actor.defs#viewerState', alias='$type', frozen=True
    )


Preferences = t.List[
    te.Annotated[
        t.Union[
            'models.AppBskyActorDefs.AdultContentPref',
            'models.AppBskyActorDefs.ContentLabelPref',
            'models.AppBskyActorDefs.SavedFeedsPref',
            'models.AppBskyActorDefs.PersonalDetailsPref',
            'models.AppBskyActorDefs.FeedViewPref',
            'models.AppBskyActorDefs.ThreadViewPref',
        ],
        Field(discriminator='py_type'),
    ]
]


class AdultContentPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    enabled: bool = None  #: Enabled.

    py_type: te.Literal['app.bsky.actor.defs#adultContentPref'] = Field(
        default='app.bsky.actor.defs#adultContentPref', alias='$type', frozen=True
    )


class ContentLabelPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    label: str  #: Label.
    visibility: str  #: Visibility.

    py_type: te.Literal['app.bsky.actor.defs#contentLabelPref'] = Field(
        default='app.bsky.actor.defs#contentLabelPref', alias='$type', frozen=True
    )


class SavedFeedsPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    pinned: t.List[str]  #: Pinned.
    saved: t.List[str]  #: Saved.

    py_type: te.Literal['app.bsky.actor.defs#savedFeedsPref'] = Field(
        default='app.bsky.actor.defs#savedFeedsPref', alias='$type', frozen=True
    )


class PersonalDetailsPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    birth_date: t.Optional[str] = Field(default=None, alias='birthDate')  #: The birth date of account owner.

    py_type: te.Literal['app.bsky.actor.defs#personalDetailsPref'] = Field(
        default='app.bsky.actor.defs#personalDetailsPref', alias='$type', frozen=True
    )


class FeedViewPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    feed: str  #: The URI of the feed, or an identifier which describes the feed.
    hide_quote_posts: t.Optional[bool] = Field(default=None, alias='hideQuotePosts')  #: Hide quote posts in the feed.
    hide_replies: t.Optional[bool] = Field(default=None, alias='hideReplies')  #: Hide replies in the feed.
    hide_replies_by_like_count: t.Optional[int] = Field(
        default=None, alias='hideRepliesByLikeCount'
    )  #: Hide replies in the feed if they do not have this number of likes.
    hide_replies_by_unfollowed: t.Optional[bool] = Field(
        default=None, alias='hideRepliesByUnfollowed'
    )  #: Hide replies in the feed if they are not by followed users.
    hide_reposts: t.Optional[bool] = Field(default=None, alias='hideReposts')  #: Hide reposts in the feed.

    py_type: te.Literal['app.bsky.actor.defs#feedViewPref'] = Field(
        default='app.bsky.actor.defs#feedViewPref', alias='$type', frozen=True
    )


class ThreadViewPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    prioritize_followed_users: t.Optional[bool] = Field(
        default=None, alias='prioritizeFollowedUsers'
    )  #: Show followed users at the top of all replies.
    sort: t.Optional[str] = None  #: Sorting mode for threads.

    py_type: te.Literal['app.bsky.actor.defs#threadViewPref'] = Field(
        default='app.bsky.actor.defs#threadViewPref', alias='$type', frozen=True
    )
