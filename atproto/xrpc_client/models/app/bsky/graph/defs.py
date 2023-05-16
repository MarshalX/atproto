##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

from typing_extensions import Literal

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
    avatar: Optional[str] = None
    indexedAt: Optional[str] = None
    viewer: Optional['models.AppBskyGraphDefs.ListViewerState'] = None

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
    avatar: Optional[str] = None
    description: Optional[str] = None
    descriptionFacets: Optional[List['models.AppBskyRichtextFacet.Main']] = None
    viewer: Optional['models.AppBskyGraphDefs.ListViewerState'] = None

    _type: str = 'app.bsky.graph.defs#listView'


@dataclass
class ListItemView(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        subject: Subject.
    """

    subject: 'models.AppBskyActorDefs.ProfileView'

    _type: str = 'app.bsky.graph.defs#listItemView'


ListPurpose = Literal['Modlist']

Modlist: Literal['modlist'] = 'modlist'


@dataclass
class ListViewerState(base.ModelBase):

    """Definition model for :obj:`app.bsky.graph.defs`.

    Attributes:
        muted: Muted.
    """

    muted: Optional[bool] = None

    _type: str = 'app.bsky.graph.defs#listViewerState'
