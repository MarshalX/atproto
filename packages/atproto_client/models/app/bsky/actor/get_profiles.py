##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.actor.getProfiles`."""

    actors: t.List[str] = Field(max_length=25)  #: Actors.


class ParamsDict(te.TypedDict):
    actors: t.List[str]  #: Actors.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.actor.getProfiles`."""

    profiles: t.List['models.AppBskyActorDefs.ProfileViewDetailed']  #: Profiles.
