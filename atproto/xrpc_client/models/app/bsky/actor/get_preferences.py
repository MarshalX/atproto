##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.actor.getPreferences`."""


class ParamsDict(te.TypedDict):
    pass


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.actor.getPreferences`."""

    preferences: 'models.AppBskyActorDefs.Preferences'  #: Preferences.
