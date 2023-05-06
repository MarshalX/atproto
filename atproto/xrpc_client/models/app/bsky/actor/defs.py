##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

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


@dataclass
class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`.

    Attributes:
        muted: Muted.
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
