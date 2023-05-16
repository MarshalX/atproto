##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.graph.list`.

    Attributes:
        purpose: Purpose.
        name: Name.
        description: Description.
        descriptionFacets: Description facets.
        avatar: Avatar.
        createdAt: Created at.
    """

    createdAt: str
    name: str
    purpose: 'models.AppBskyGraphDefs.ListPurpose'
    avatar: Optional[BlobRef] = None
    description: Optional[str] = None
    descriptionFacets: Optional[List['models.AppBskyRichtextFacet.Main']] = None

    _type: str = 'app.bsky.graph.list'
