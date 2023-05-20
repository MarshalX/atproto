##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.actor.searchActors`.

    Attributes:
        term: Term.
        limit: Limit.
        cursor: Cursor.
    """

    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None
    term: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.actor.searchActors`.

    Attributes:
        cursor: Cursor.
        actors: Actors.
    """

    actors: t.List['models.AppBskyActorDefs.ProfileView']
    cursor: t.Optional[str] = None
