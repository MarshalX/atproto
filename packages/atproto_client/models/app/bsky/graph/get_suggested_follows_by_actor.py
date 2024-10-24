##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.graph.getSuggestedFollowsByActor`."""

    actor: str  #: Actor.


class ParamsDict(t.TypedDict):
    actor: str  #: Actor.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.graph.getSuggestedFollowsByActor`."""

    suggestions: t.List['models.AppBskyActorDefs.ProfileView']  #: Suggestions.
    is_fallback: t.Optional[bool] = (
        False  #: If true, response has fallen-back to generic results, and is not scoped using relativeToDid.
    )
