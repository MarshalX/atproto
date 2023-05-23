##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.graph.list`."""

    createdAt: str  #: Created at.
    name: str  #: Name.
    purpose: 'models.AppBskyGraphDefs.ListPurpose'  #: Purpose.
    avatar: t.Optional[BlobRef] = None  #: Avatar.
    description: t.Optional[str] = None  #: Description.
    descriptionFacets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.

    _type: str = 'app.bsky.graph.list'
