##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.moderation.updateActorAccess`."""

    actor: str  #: Actor.
    allow_access: bool  #: Allow access.
    ref: t.Optional[str] = None  #: Ref.


class DataDict(t.TypedDict):
    actor: str  #: Actor.
    allow_access: bool  #: Allow access.
    ref: te.NotRequired[t.Optional[str]]  #: Ref.
