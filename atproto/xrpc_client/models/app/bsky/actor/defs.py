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
class ProfileViewBasic(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    displayName: t.Optional[str] = None  #: Display name.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    _type: str = 'app.bsky.actor.defs#profileViewBasic'


@dataclass
class ProfileView(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.
    indexedAt: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    _type: str = 'app.bsky.actor.defs#profileView'


@dataclass
class ProfileViewDetailed(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    avatar: t.Optional[str] = None  #: Avatar.
    banner: t.Optional[str] = None  #: Banner.
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.
    followersCount: t.Optional[int] = None  #: Followers count.
    followsCount: t.Optional[int] = None  #: Follows count.
    indexedAt: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    postsCount: t.Optional[int] = None  #: Posts count.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    _type: str = 'app.bsky.actor.defs#profileViewDetailed'


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    blockedBy: t.Optional[bool] = None  #: Blocked by.
    blocking: t.Optional[str] = None  #: Blocking.
    followedBy: t.Optional[str] = None  #: Followed by.
    following: t.Optional[str] = None  #: Following.
    muted: t.Optional[bool] = None  #: Muted.
    mutedByList: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Muted by list.

    _type: str = 'app.bsky.actor.defs#viewerState'


Preferences = t.List[
    t.Union[
        'models.AppBskyActorDefs.AdultContentPref',
        'models.AppBskyActorDefs.ContentLabelPref',
        'models.AppBskyActorDefs.SavedFeedsPref',
        't.Dict[str, t.Any]',
    ]
]


@dataclass
class AdultContentPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    enabled: bool  #: Enabled.

    _type: str = 'app.bsky.actor.defs#adultContentPref'


@dataclass
class ContentLabelPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    label: str  #: Label.
    visibility: str  #: Visibility.

    _type: str = 'app.bsky.actor.defs#contentLabelPref'


@dataclass
class SavedFeedsPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    pinned: t.List[str]  #: Pinned.
    saved: t.List[str]  #: Saved.

    _type: str = 'app.bsky.actor.defs#savedFeedsPref'
