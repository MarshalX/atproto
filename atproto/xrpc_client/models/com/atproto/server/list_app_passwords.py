##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.listAppPasswords`.

    Attributes:
        passwords: Passwords.
    """

    passwords: List['models.ComAtprotoServerListAppPasswords.AppPassword']


@dataclass
class AppPassword(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.listAppPasswords`.

    Attributes:
        name: Name.
        createdAt: Created at.
    """

    createdAt: str
    name: str
