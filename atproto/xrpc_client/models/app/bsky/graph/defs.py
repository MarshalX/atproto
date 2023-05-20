##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

import typing_extensions as te

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class ListViewBasic(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        uri: Uri.
        name: Name.
        purpose: Purpose.
        avatar: Avatar.
        viewer: Viewer.
        indexedAt: Indexed at.
    """

    name: str
    purpose: 'models.AppBskyGraphDefs.ListPurpose'
    uri: str
    avatar: t.Optional[str] = None
    indexedAt: t.Optional[str] = None
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None

    _type: str = 'app.bsky.graph.defs#listViewBasic'


@dataclass
class ListView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        uri: Uri.
        creator: Creator.
        name: Name.
        purpose: Purpose.
        description: Description.
        descriptionFacets: Description facets.
        avatar: Avatar.
        viewer: Viewer.
        indexedAt: Indexed at.
    """

    creator: 'models.AppBskyActorDefs.ProfileView'
    indexedAt: str
    name: str
    purpose: 'models.AppBskyGraphDefs.ListPurpose'
    uri: str
    avatar: t.Optional[str] = None
    description: t.Optional[str] = None
    descriptionFacets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None
    viewer: t.Optional['models.AppBskyGraphDefs.ListViewerState'] = None

    _type: str = 'app.bsky.graph.defs#listView'


@dataclass
class ListItemView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        subject: Subject.
    """

    subject: 'models.AppBskyActorDefs.ProfileView'

    _type: str = 'app.bsky.graph.defs#listItemView'


ListPurpose = te.Literal['Modlist']

Modlist: te.Literal['modlist'] = 'modlist'


@dataclass
class ListViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        muted: Muted.
    """

    muted: t.Optional[bool] = None

    _type: str = 'app.bsky.graph.defs#listViewerState'
