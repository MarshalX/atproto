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


class ProfileViewBasic(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileViewBasic'] = Field(
        default='app.bsky.actor.defs#profileViewBasic', alias='$type', frozen=True
    )


class ProfileView(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    indexed_at: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileView'] = Field(
        default='app.bsky.actor.defs#profileView', alias='$type', frozen=True
    )


class ProfileViewDetailed(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    banner: t.Optional[str] = None  #: Banner.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    followers_count: t.Optional[int] = None  #: Followers count.
    follows_count: t.Optional[int] = None  #: Follows count.
    indexed_at: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    posts_count: t.Optional[int] = None  #: Posts count.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileViewDetailed'] = Field(
        default='app.bsky.actor.defs#profileViewDetailed', alias='$type', frozen=True
    )


class ProfileAssociated(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    feedgens: t.Optional[int] = None  #: Feedgens.
    labeler: t.Optional[bool] = None  #: Labeler.
    lists: t.Optional[int] = None  #: Lists.

    py_type: te.Literal['app.bsky.actor.defs#profileAssociated'] = Field(
        default='app.bsky.actor.defs#profileAssociated', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. Metadata about the requesting account's relationship with the subject account. Only has meaningful content for authed requests."""

    blocked_by: t.Optional[bool] = None  #: Blocked by.
    blocking: t.Optional[str] = None  #: Blocking.
    blocking_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Blocking by list.
    followed_by: t.Optional[str] = None  #: Followed by.
    following: t.Optional[str] = None  #: Following.
    muted: t.Optional[bool] = None  #: Muted.
    muted_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Muted by list.

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
            'models.AppBskyActorDefs.InterestsPref',
            'models.AppBskyActorDefs.MutedWordsPref',
            'models.AppBskyActorDefs.HiddenPostsPref',
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
    labeler_did: t.Optional[str] = None  #: Which labeler does this preference apply to? If undefined, applies globally.

    py_type: te.Literal['app.bsky.actor.defs#contentLabelPref'] = Field(
        default='app.bsky.actor.defs#contentLabelPref', alias='$type', frozen=True
    )


class SavedFeedsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    pinned: t.List[str]  #: Pinned.
    saved: t.List[str]  #: Saved.
    timeline_index: t.Optional[int] = None  #: Timeline index.

    py_type: te.Literal['app.bsky.actor.defs#savedFeedsPref'] = Field(
        default='app.bsky.actor.defs#savedFeedsPref', alias='$type', frozen=True
    )


class PersonalDetailsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    birth_date: t.Optional[str] = None  #: The birth date of account owner.

    py_type: te.Literal['app.bsky.actor.defs#personalDetailsPref'] = Field(
        default='app.bsky.actor.defs#personalDetailsPref', alias='$type', frozen=True
    )


class FeedViewPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    feed: str  #: The URI of the feed, or an identifier which describes the feed.
    hide_quote_posts: t.Optional[bool] = None  #: Hide quote posts in the feed.
    hide_replies: t.Optional[bool] = None  #: Hide replies in the feed.
    hide_replies_by_like_count: t.Optional[
        int
    ] = None  #: Hide replies in the feed if they do not have this number of likes.
    hide_replies_by_unfollowed: t.Optional[bool] = None  #: Hide replies in the feed if they are not by followed users.
    hide_reposts: t.Optional[bool] = None  #: Hide reposts in the feed.

    py_type: te.Literal['app.bsky.actor.defs#feedViewPref'] = Field(
        default='app.bsky.actor.defs#feedViewPref', alias='$type', frozen=True
    )


class ThreadViewPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    prioritize_followed_users: t.Optional[bool] = None  #: Show followed users at the top of all replies.
    sort: t.Optional[str] = None  #: Sorting mode for threads.

    py_type: te.Literal['app.bsky.actor.defs#threadViewPref'] = Field(
        default='app.bsky.actor.defs#threadViewPref', alias='$type', frozen=True
    )


class InterestsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    tags: t.List[str] = Field(
        max_length=100
    )  #: A list of tags which describe the account owner's interests gathered during onboarding.

    py_type: te.Literal['app.bsky.actor.defs#interestsPref'] = Field(
        default='app.bsky.actor.defs#interestsPref', alias='$type', frozen=True
    )


MutedWordTarget = t.Union[te.Literal['content'], te.Literal['tag']]  #: Muted word target


class MutedWord(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. A word that the account owner has muted."""

    targets: t.List['models.AppBskyActorDefs.MutedWordTarget']  #: The intended targets of the muted word.
    value: str = Field(max_length=10000)  #: The muted word itself.

    py_type: te.Literal['app.bsky.actor.defs#mutedWord'] = Field(
        default='app.bsky.actor.defs#mutedWord', alias='$type', frozen=True
    )


class MutedWordsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    items: t.List['models.AppBskyActorDefs.MutedWord']  #: A list of words the account owner has muted.

    py_type: te.Literal['app.bsky.actor.defs#mutedWordsPref'] = Field(
        default='app.bsky.actor.defs#mutedWordsPref', alias='$type', frozen=True
    )


class HiddenPostsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    items: t.List[str]  #: A list of URIs of posts the account owner has hidden.

    py_type: te.Literal['app.bsky.actor.defs#hiddenPostsPref'] = Field(
        default='app.bsky.actor.defs#hiddenPostsPref', alias='$type', frozen=True
    )


class LabelersPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    labelers: t.List['models.AppBskyActorDefs.LabelerPrefItem']  #: Labelers.

    py_type: te.Literal['app.bsky.actor.defs#labelersPref'] = Field(
        default='app.bsky.actor.defs#labelersPref', alias='$type', frozen=True
    )


class LabelerPrefItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.

    py_type: te.Literal['app.bsky.actor.defs#labelerPrefItem'] = Field(
        default='app.bsky.actor.defs#labelerPrefItem', alias='$type', frozen=True
    )
