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

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        did: Did.
        handle: Handle.
        displayName: Display name.
        avatar: Avatar.
        viewer: Viewer.
        labels: Labels.
    """

    did: str
    handle: str
    avatar: t.Optional[str] = None
    displayName: t.Optional[str] = None
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None

    _type: str = 'app.bsky.actor.defs#profileViewBasic'


@dataclass
class ProfileView(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        did: Did.
        handle: Handle.
        displayName: Display name.
        description: Description.
        avatar: Avatar.
        indexedAt: Indexed at.
        viewer: Viewer.
        labels: Labels.
    """

    did: str
    handle: str
    avatar: t.Optional[str] = None
    description: t.Optional[str] = None
    displayName: t.Optional[str] = None
    indexedAt: t.Optional[str] = None
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None

    _type: str = 'app.bsky.actor.defs#profileView'


@dataclass
class ProfileViewDetailed(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        did: Did.
        handle: Handle.
        displayName: Display name.
        description: Description.
        avatar: Avatar.
        banner: Banner.
        followersCount: Followers count.
        followsCount: Follows count.
        postsCount: Posts count.
        indexedAt: Indexed at.
        viewer: Viewer.
        labels: Labels.
    """

    did: str
    handle: str
    avatar: t.Optional[str] = None
    banner: t.Optional[str] = None
    description: t.Optional[str] = None
    displayName: t.Optional[str] = None
    followersCount: t.Optional[int] = None
    followsCount: t.Optional[int] = None
    indexedAt: t.Optional[str] = None
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None
    postsCount: t.Optional[int] = None
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None

    _type: str = 'app.bsky.actor.defs#profileViewDetailed'


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        muted: Muted.
        mutedByList: Muted by list.
        blockedBy: Blocked by.
        blocking: Blocking.
        following: Following.
        followedBy: Followed by.
    """

    blockedBy: t.Optional[bool] = None
    blocking: t.Optional[str] = None
    followedBy: t.Optional[str] = None
    following: t.Optional[str] = None
    muted: t.Optional[bool] = None
    mutedByList: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None

    _type: str = 'app.bsky.actor.defs#viewerState'


Preferences = t.List[
    t.Union[
        'models.AppBskyActorDefs.AdultContentPref', 'models.AppBskyActorDefs.ContentLabelPref', 't.Dict[str, t.Any]'
    ]
]


@dataclass
class AdultContentPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        enabled: Enabled.
    """

    enabled: bool

    _type: str = 'app.bsky.actor.defs#adultContentPref'


@dataclass
class ContentLabelPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        label: Label.
        visibility: Visibility.
    """

    label: str
    visibility: str

    _type: str = 'app.bsky.actor.defs#contentLabelPref'
