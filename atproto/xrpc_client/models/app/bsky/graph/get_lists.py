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

    """Parameters model for :obj:`app.bsky.graph.getLists`.

    Attributes:
        actor: Actor.
        limit: Limit.
        cursor: Cursor.
    """

    actor: str
    cursor: Optional[str] = None
    limit: Optional[int] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.graph.getLists`.

    Attributes:
        cursor: Cursor.
        lists: Lists.
    """

    lists: List['models.AppBskyGraphDefs.ListView']
    cursor: Optional[str] = None
