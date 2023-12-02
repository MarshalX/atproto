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


class ListViewBasic(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    name: str = Field(min_length=1, max_length=64)  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    indexed_at: t.Optional[str] = Field(default=None, alias='indexedAt')  #: Indexed at.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.graph.defs#listViewBasic'] = Field(
        default='app.bsky.graph.defs#listViewBasic', alias='$type', frozen=True
    )


class ListView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    name: str = Field(min_length=1, max_length=64)  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = Field(
        default=None, alias='descriptionFacets'
    )  #: Description facets.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.graph.defs#listView'] = Field(
        default='app.bsky.graph.defs#listView', alias='$type', frozen=True
    )


class ListItemView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    subject: 'models.AppBskyActorDefs.ProfileView'  #: Subject.
    uri: str  #: Uri.

    py_type: te.Literal['app.bsky.graph.defs#listItemView'] = Field(
        default='app.bsky.graph.defs#listItemView', alias='$type', frozen=True
    )


ListPurpose = t.Union['models.AppBskyGraphDefs.Modlist', 'models.AppBskyGraphDefs.Curatelist']  #: List purpose

Modlist = te.Literal[
    'app.bsky.graph.defs#modlist'
]  #: A list of actors to apply an aggregate moderation action (mute/block) on.

Curatelist = te.Literal[
    'app.bsky.graph.defs#curatelist'
]  #: A list of actors used for curation purposes such as list feeds or interaction gating.


class ListViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    blocked: t.Optional[str] = None  #: Blocked.
    muted: t.Optional[bool] = None  #: Muted.

    py_type: te.Literal['app.bsky.graph.defs#listViewerState'] = Field(
        default='app.bsky.graph.defs#listViewerState', alias='$type', frozen=True
    )
