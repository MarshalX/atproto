##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`app.bsky.graph.unmuteActor`."""

    actor: str  #: Actor.


class DataDict(te.TypedDict):
    actor: str  #: Actor.
