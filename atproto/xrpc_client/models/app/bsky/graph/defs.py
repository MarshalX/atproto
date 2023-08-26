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
    name: str  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    indexedAt: t.Optional[str] = None  #: Indexed at.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.graph.defs#listViewBasic'] = Field(
        default='app.bsky.graph.defs#listViewBasic', alias='$type'
    )


class ListView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    cid: str  #: Cid.
    creator: 'models.AppBskyActorDefs.ProfileView'  #: Creator.
    indexedAt: str  #: Indexed at.
    name: str  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    uri: str  #: Uri.
    avatar: t.Optional[str] = None  #: Avatar.
    description: t.Optional[str] = None  #: Description.
    descriptionFacets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None  #: Viewer.

    py_type: te.Literal['app.bsky.graph.defs#listView'] = Field(default='app.bsky.graph.defs#listView', alias='$type')


class ListItemView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    subject: 'models.AppBskyActorDefs.ProfileView'  #: Subject.

    py_type: te.Literal['app.bsky.graph.defs#listItemView'] = Field(
        default='app.bsky.graph.defs#listItemView', alias='$type'
    )


ListPurpose = te.Literal['Modlist']

Modlist: te.Literal['modlist'] = 'modlist'


class ListViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`."""

    muted: t.Optional[bool] = None  #: Muted.

    py_type: te.Literal['app.bsky.graph.defs#listViewerState'] = Field(
        default='app.bsky.graph.defs#listViewerState', alias='$type'
    )
