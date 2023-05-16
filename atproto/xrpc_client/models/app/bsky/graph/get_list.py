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
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.graph.getList`.

    Attributes:
        list: List.
        limit: Limit.
        cursor: Cursor.
    """

    list: str
    cursor: Optional[str] = None
    limit: Optional[int] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.graph.getList`.

    Attributes:
        cursor: Cursor.
        list: List.
        items: Items.
    """

    items: List['models.AppBskyGraphDefs.ListItemView']
    list: 'models.AppBskyGraphDefs.ListView'
    cursor: Optional[str] = None
