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
from atproto_client.models import base


class ProfileViewBasic(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    created_at: t.Optional[str] = None  #: Created at.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.actor.defs#profileViewBasic'] = Field(
        default='app.bsky.actor.defs#profileViewBasic', alias='$type', frozen=True
    )


class ProfileView(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    created_at: t.Optional[str] = None  #: Created at.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    indexed_at: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.actor.defs#profileView'] = Field(
        default='app.bsky.actor.defs#profileView', alias='$type', frozen=True
    )


class ProfileViewDetailed(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    associated: t.Optional['models.AppBskyActorDefs.ProfileAssociated'] = None  #: Associated.
    avatar: t.Optional[str] = None  #: Avatar.
    banner: t.Optional[str] = None  #: Banner.
    created_at: t.Optional[str] = None  #: Created at.
    description: t.Optional[str] = Field(default=None, max_length=2560)  #: Description.
    display_name: t.Optional[str] = Field(default=None, max_length=640)  #: Display name.
    followers_count: t.Optional[int] = None  #: Followers count.
    follows_count: t.Optional[int] = None  #: Follows count.
    indexed_at: t.Optional[str] = None  #: Indexed at.
    joined_via_starter_pack: t.Optional[
        'models.AppBskyGraphDefs.StarterPackViewBasic'
    ] = None  #: Joined via starter pack.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    posts_count: t.Optional[int] = None  #: Posts count.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.actor.defs#profileViewDetailed'] = Field(
        default='app.bsky.actor.defs#profileViewDetailed', alias='$type', frozen=True
    )


class ProfileAssociated(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    chat: t.Optional['models.AppBskyActorDefs.ProfileAssociatedChat'] = None  #: Chat.
    feedgens: t.Optional[int] = None  #: Feedgens.
    labeler: t.Optional[bool] = None  #: Labeler.
    lists: t.Optional[int] = None  #: Lists.
    starter_packs: t.Optional[int] = None  #: Starter packs.

    py_type: t.Literal['app.bsky.actor.defs#profileAssociated'] = Field(
        default='app.bsky.actor.defs#profileAssociated', alias='$type', frozen=True
    )


class ProfileAssociatedChat(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    allow_incoming: t.Union[t.Literal['all'], t.Literal['none'], t.Literal['following'], str]  #: Allow incoming.

    py_type: t.Literal['app.bsky.actor.defs#profileAssociatedChat'] = Field(
        default='app.bsky.actor.defs#profileAssociatedChat', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. Metadata about the requesting account's relationship with the subject account. Only has meaningful content for authed requests."""

    blocked_by: t.Optional[bool] = None  #: Blocked by.
    blocking: t.Optional[str] = None  #: Blocking.
    blocking_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Blocking by list.
    followed_by: t.Optional[str] = None  #: Followed by.
    following: t.Optional[str] = None  #: Following.
    known_followers: t.Optional['models.AppBskyActorDefs.KnownFollowers'] = None  #: Known followers.
    muted: t.Optional[bool] = None  #: Muted.
    muted_by_list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Muted by list.

    py_type: t.Literal['app.bsky.actor.defs#viewerState'] = Field(
        default='app.bsky.actor.defs#viewerState', alias='$type', frozen=True
    )


class KnownFollowers(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. The subject's followers whom you also follow."""

    count: int  #: Count.
    followers: t.List['models.AppBskyActorDefs.ProfileViewBasic'] = Field(min_length=0, max_length=5)  #: Followers.

    py_type: t.Literal['app.bsky.actor.defs#knownFollowers'] = Field(
        default='app.bsky.actor.defs#knownFollowers', alias='$type', frozen=True
    )


Preferences = t.List[
    te.Annotated[
        t.Union[
            'models.AppBskyActorDefs.AdultContentPref',
            'models.AppBskyActorDefs.ContentLabelPref',
            'models.AppBskyActorDefs.SavedFeedsPref',
            'models.AppBskyActorDefs.SavedFeedsPrefV2',
            'models.AppBskyActorDefs.PersonalDetailsPref',
            'models.AppBskyActorDefs.FeedViewPref',
            'models.AppBskyActorDefs.ThreadViewPref',
            'models.AppBskyActorDefs.InterestsPref',
            'models.AppBskyActorDefs.MutedWordsPref',
            'models.AppBskyActorDefs.HiddenPostsPref',
            'models.AppBskyActorDefs.BskyAppStatePref',
            'models.AppBskyActorDefs.LabelersPref',
        ],
        Field(discriminator='py_type'),
    ]
]


class AdultContentPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    enabled: bool = False  #: Enabled.

    py_type: t.Literal['app.bsky.actor.defs#adultContentPref'] = Field(
        default='app.bsky.actor.defs#adultContentPref', alias='$type', frozen=True
    )


class ContentLabelPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    label: str  #: Label.
    visibility: t.Union[
        t.Literal['ignore'], t.Literal['show'], t.Literal['warn'], t.Literal['hide'], str
    ]  #: Visibility.
    labeler_did: t.Optional[str] = None  #: Which labeler does this preference apply to? If undefined, applies globally.

    py_type: t.Literal['app.bsky.actor.defs#contentLabelPref'] = Field(
        default='app.bsky.actor.defs#contentLabelPref', alias='$type', frozen=True
    )


class SavedFeed(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    id: str  #: Id.
    pinned: bool  #: Pinned.
    type: t.Union[t.Literal['feed'], t.Literal['list'], t.Literal['timeline'], str]  #: Type.
    value: str  #: Value.

    py_type: t.Literal['app.bsky.actor.defs#savedFeed'] = Field(
        default='app.bsky.actor.defs#savedFeed', alias='$type', frozen=True
    )


class SavedFeedsPrefV2(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    items: t.List['models.AppBskyActorDefs.SavedFeed']  #: Items.

    py_type: t.Literal['app.bsky.actor.defs#savedFeedsPrefV2'] = Field(
        default='app.bsky.actor.defs#savedFeedsPrefV2', alias='$type', frozen=True
    )


class SavedFeedsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    pinned: t.List[str]  #: Pinned.
    saved: t.List[str]  #: Saved.
    timeline_index: t.Optional[int] = None  #: Timeline index.

    py_type: t.Literal['app.bsky.actor.defs#savedFeedsPref'] = Field(
        default='app.bsky.actor.defs#savedFeedsPref', alias='$type', frozen=True
    )


class PersonalDetailsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    birth_date: t.Optional[str] = None  #: The birth date of account owner.

    py_type: t.Literal['app.bsky.actor.defs#personalDetailsPref'] = Field(
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
    hide_replies_by_unfollowed: t.Optional[bool] = True  #: Hide replies in the feed if they are not by followed users.
    hide_reposts: t.Optional[bool] = None  #: Hide reposts in the feed.

    py_type: t.Literal['app.bsky.actor.defs#feedViewPref'] = Field(
        default='app.bsky.actor.defs#feedViewPref', alias='$type', frozen=True
    )


class ThreadViewPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    prioritize_followed_users: t.Optional[bool] = None  #: Show followed users at the top of all replies.
    sort: t.Optional[
        t.Union[t.Literal['oldest'], t.Literal['newest'], t.Literal['most-likes'], t.Literal['random'], str]
    ] = None  #: Sorting mode for threads.

    py_type: t.Literal['app.bsky.actor.defs#threadViewPref'] = Field(
        default='app.bsky.actor.defs#threadViewPref', alias='$type', frozen=True
    )


class InterestsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    tags: t.List[str] = Field(
        max_length=100
    )  #: A list of tags which describe the account owner's interests gathered during onboarding.

    py_type: t.Literal['app.bsky.actor.defs#interestsPref'] = Field(
        default='app.bsky.actor.defs#interestsPref', alias='$type', frozen=True
    )


MutedWordTarget = t.Union[t.Literal['content'], t.Literal['tag'], str]  #: Muted word target


class MutedWord(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. A word that the account owner has muted."""

    targets: t.List['models.AppBskyActorDefs.MutedWordTarget']  #: The intended targets of the muted word.
    value: str = Field(max_length=10000)  #: The muted word itself.
    actor_target: t.Optional[
        t.Union[t.Literal['all'], t.Literal['exclude-following'], str]
    ] = 'all'  #: Groups of users to apply the muted word to. If undefined, applies to all users.
    expires_at: t.Optional[
        str
    ] = None  #: The date and time at which the muted word will expire and no longer be applied.
    id: t.Optional[str] = None  #: Id.

    py_type: t.Literal['app.bsky.actor.defs#mutedWord'] = Field(
        default='app.bsky.actor.defs#mutedWord', alias='$type', frozen=True
    )


class MutedWordsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    items: t.List['models.AppBskyActorDefs.MutedWord']  #: A list of words the account owner has muted.

    py_type: t.Literal['app.bsky.actor.defs#mutedWordsPref'] = Field(
        default='app.bsky.actor.defs#mutedWordsPref', alias='$type', frozen=True
    )


class HiddenPostsPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    items: t.List[str]  #: A list of URIs of posts the account owner has hidden.

    py_type: t.Literal['app.bsky.actor.defs#hiddenPostsPref'] = Field(
        default='app.bsky.actor.defs#hiddenPostsPref', alias='$type', frozen=True
    )


class LabelersPref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    labelers: t.List['models.AppBskyActorDefs.LabelerPrefItem']  #: Labelers.

    py_type: t.Literal['app.bsky.actor.defs#labelersPref'] = Field(
        default='app.bsky.actor.defs#labelersPref', alias='$type', frozen=True
    )


class LabelerPrefItem(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.

    py_type: t.Literal['app.bsky.actor.defs#labelerPrefItem'] = Field(
        default='app.bsky.actor.defs#labelerPrefItem', alias='$type', frozen=True
    )


class BskyAppStatePref(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. A grab bag of state that's specific to the bsky.app program. Third-party apps shouldn't use this."""

    active_progress_guide: t.Optional['models.AppBskyActorDefs.BskyAppProgressGuide'] = None  #: Active progress guide.
    nuxs: t.Optional[t.List['models.AppBskyActorDefs.Nux']] = Field(
        default=None, max_length=100
    )  #: Storage for NUXs the user has encountered.
    queued_nudges: t.Optional[t.List[str]] = Field(
        default=None, max_length=1000
    )  #: An array of tokens which identify nudges (modals, popups, tours, highlight dots) that should be shown to the user.

    py_type: t.Literal['app.bsky.actor.defs#bskyAppStatePref'] = Field(
        default='app.bsky.actor.defs#bskyAppStatePref', alias='$type', frozen=True
    )


class BskyAppProgressGuide(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. If set, an active progress guide. Once completed, can be set to undefined. Should have unspecced fields tracking progress."""

    guide: str = Field(max_length=100)  #: Guide.

    py_type: t.Literal['app.bsky.actor.defs#bskyAppProgressGuide'] = Field(
        default='app.bsky.actor.defs#bskyAppProgressGuide', alias='$type', frozen=True
    )


class Nux(base.ModelBase):
    """Definition model for :obj:`app.bsky.actor.defs`. A new user experiences (NUX) storage object."""

    completed: bool = False  #: Completed.
    id: str = Field(max_length=100)  #: Id.
    data: t.Optional[str] = Field(
        default=None, max_length=3000
    )  #: Arbitrary data for the NUX. The structure is defined by the NUX itself. Limited to 300 characters.
    expires_at: t.Optional[
        str
    ] = None  #: The date and time at which the NUX will expire and should be considered completed.

    py_type: t.Literal['app.bsky.actor.defs#nux'] = Field(default='app.bsky.actor.defs#nux', alias='$type', frozen=True)
