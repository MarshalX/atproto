##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.actor.getProfile`."""

    actor: str  #: Actor.


#: Response reference to :obj:`models.AppBskyActorDefs.ProfileViewDetailed` model.
ResponseRef = models.AppBskyActorDefs.ProfileViewDetailed
