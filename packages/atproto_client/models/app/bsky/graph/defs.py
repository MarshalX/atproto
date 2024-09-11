##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class ListViewBasic(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    name: str = Field(min_length=1, max_length=64)  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    indexed_at: t.Optional[str] = None  #: Indexed at.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    list_item_count: t.Optional[int] = Field(default=None, ge=0)  #: List item count.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.graph.defs#listViewBasic'] = Field(
        default='app.bsky.graph.defs#listViewBasic', alias='$type', frozen=True
    )


class ListView(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    indexed_at: str  #: Indexed at.
    name: str = Field(min_length=1, max_length=64)  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    list_item_count: t.Optional[int] = Field(default=None, ge=0)  #: List item count.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: t.Literal['app.bsky.graph.defs#listView'] = Field(
        default='app.bsky.graph.defs#listView', alias='$type', frozen=True
    )


class ListItemView(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    subject: 'models.AppBskyActorDefs.ProfileView'  #: Subject.
    uri: str  #: Uri.

    py_type: t.Literal['app.bsky.graph.defs#listItemView'] = Field(
        default='app.bsky.graph.defs#listItemView', alias='$type', frozen=True
    )


class StarterPackView(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Creator.
    indexed_at: str  #: Indexed at.
    record: 'UnknownType'  #: Record.
    uri: str  #: Uri.
    feeds: t.Optional[t.List['models.AppBskyFeedDefs.GeneratorView']] = Field(default=None, max_length=3)  #: Feeds.
    joined_all_time_count: t.Optional[int] = Field(default=None, ge=0)  #: Joined all time count.
    joined_week_count: t.Optional[int] = Field(default=None, ge=0)  #: Joined week count.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    list: t.Optional['models.AppBskyGraphDefs.ListViewBasic'] = None  #: List.
    list_items_sample: t.Optional[t.List['models.AppBskyGraphDefs.ListItemView']] = Field(
        default=None, max_length=12
    )  #: List items sample.

    py_type: t.Literal['app.bsky.graph.defs#starterPackView'] = Field(
        default='app.bsky.graph.defs#starterPackView', alias='$type', frozen=True
    )


class StarterPackViewBasic(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Creator.
    indexed_at: str  #: Indexed at.
    record: 'UnknownType'  #: Record.
    uri: str  #: Uri.
    joined_all_time_count: t.Optional[int] = Field(default=None, ge=0)  #: Joined all time count.
    joined_week_count: t.Optional[int] = Field(default=None, ge=0)  #: Joined week count.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    list_item_count: t.Optional[int] = Field(default=None, ge=0)  #: List item count.

    py_type: t.Literal['app.bsky.graph.defs#starterPackViewBasic'] = Field(
        default='app.bsky.graph.defs#starterPackViewBasic', alias='$type', frozen=True
    )


ListPurpose = t.Union[
    'models.AppBskyGraphDefs.Modlist',
    'models.AppBskyGraphDefs.Curatelist',
    'models.AppBskyGraphDefs.Referencelist',
    str,
]  #: List purpose

Modlist = t.Literal[
    'app.bsky.graph.defs#modlist'
]  #: A list of actors to apply an aggregate moderation action (mute/block) on.

Curatelist = t.Literal[
    'app.bsky.graph.defs#curatelist'
]  #: A list of actors used for curation purposes such as list feeds or interaction gating.

Referencelist = t.Literal[
    'app.bsky.graph.defs#referencelist'
]  #: A list of actors used for only for reference purposes such as within a starter pack.


class ListViewerState(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`."""

    blocked: t.Optional[str] = None  #: Blocked.
    muted: t.Optional[bool] = None  #: Muted.

    py_type: t.Literal['app.bsky.graph.defs#listViewerState'] = Field(
        default='app.bsky.graph.defs#listViewerState', alias='$type', frozen=True
    )


class NotFoundActor(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`. indicates that a handle or DID could not be resolved."""

    actor: str  #: Actor.
    not_found: bool = Field(frozen=True)  #: Not found.

    py_type: t.Literal['app.bsky.graph.defs#notFoundActor'] = Field(
        default='app.bsky.graph.defs#notFoundActor', alias='$type', frozen=True
    )


class Relationship(base.ModelBase):
    """Definition model for :obj:`app.bsky.graph.defs`. lists the bi-directional graph relationships between one actor (not indicated in the object), and the target actors (the DID included in the object)."""

    did: str  #: Did.
    followed_by: t.Optional[
        str
    ] = None  #: if the actor is followed by this DID, contains the AT-URI of the follow record.
    following: t.Optional[str] = None  #: if the actor follows this DID, this is the AT-URI of the follow record.

    py_type: t.Literal['app.bsky.graph.defs#relationship'] = Field(
        default='app.bsky.graph.defs#relationship', alias='$type', frozen=True
    )
