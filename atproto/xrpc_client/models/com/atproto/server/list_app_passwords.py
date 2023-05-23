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
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.listAppPasswords`."""

    passwords: t.List['models.ComAtprotoServerListAppPasswords.AppPassword']  #: Passwords.


@dataclass
class AppPassword(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.listAppPasswords`."""

    createdAt: str  #: Created at.
    name: str  #: Name.

    _type: str = 'com.atproto.server.listAppPasswords#appPassword'
