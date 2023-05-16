##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional, Union

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
    avatar: Optional[str] = None
    displayName: Optional[str] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None
    viewer: Optional['models.AppBskyActorDefs.ViewerState'] = None

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
    avatar: Optional[str] = None
    description: Optional[str] = None
    displayName: Optional[str] = None
    indexedAt: Optional[str] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None
    viewer: Optional['models.AppBskyActorDefs.ViewerState'] = None

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
    avatar: Optional[str] = None
    banner: Optional[str] = None
    description: Optional[str] = None
    displayName: Optional[str] = None
    followersCount: Optional[int] = None
    followsCount: Optional[int] = None
    indexedAt: Optional[str] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None
    postsCount: Optional[int] = None
    viewer: Optional['models.AppBskyActorDefs.ViewerState'] = None

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

    blockedBy: Optional[bool] = None
    blocking: Optional[str] = None
    followedBy: Optional[str] = None
    following: Optional[str] = None
    muted: Optional[bool] = None
    mutedByList: Optional['models.AppBskyGraphDefs.ListViewBasic'] = None

    _type: str = 'app.bsky.actor.defs#viewerState'


Preferences = List[
    Union['models.AppBskyActorDefs.AdultContentPref', 'models.AppBskyActorDefs.ContentLabelPref', 'Dict[str, Any]']
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
