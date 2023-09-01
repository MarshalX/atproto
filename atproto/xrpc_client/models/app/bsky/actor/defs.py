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
    displayName: t.Optional[str] = None  #: Display name.
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
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.
    indexedAt: t.Optional[str] = None  #: Indexed at.
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
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.
    followersCount: t.Optional[int] = None  #: Followers count.
    followsCount: t.Optional[int] = None  #: Follows count.
    indexedAt: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    postsCount: t.Optional[int] = None  #: Posts count.
    viewer: t.Optional['models.AppBskyActorDefs.ViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.actor.defs#profileViewDetailed'] = Field(
        default='app.bsky.actor.defs#profileViewDetailed', alias='$type', frozen=True
    )


class ViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    blockedBy: t.Optional[bool] = None  #: Blocked by.
    blocking: t.Optional[str] = None  #: Blocking.
    followedBy: t.Optional[str] = None  #: Followed by.
    following: t.Optional[str] = None  #: Following.
    muted: t.Optional[bool] = None  #: Muted.
    mutedByList: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: Muted by list.

    py_type: te.Literal['app.bsky.actor.defs#viewerState'] = Field(
        default='app.bsky.actor.defs#viewerState', alias='$type', frozen=True
    )


Preferences = t.List[
    te.Annotated[
        t.Union[
            'models.AppBskyActorDefs.AdultContentPref',
            'models.AppBskyActorDefs.ContentLabelPref',
            'models.AppBskyActorDefs.SavedFeedsPref',
        ],
        Field(discriminator='py_type'),
    ]
]


class AdultContentPref(base.ModelBase):

    """Definition model for :obj:`app.bsky.actor.defs`."""

    enabled: bool  #: Enabled.

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
