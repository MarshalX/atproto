##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.actor.getProfile`."""

    actor: str  #: Handle or DID of account to fetch profile of.


class ParamsDict(t.TypedDict):
    actor: str  #: Handle or DID of account to fetch profile of.
