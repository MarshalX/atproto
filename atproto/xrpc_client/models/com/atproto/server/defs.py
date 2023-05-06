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
class InviteCode(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.defs`.

    Attributes:
        code: Code.
        available: Available.
        disabled: Disabled.
        forAccount: For account.
        createdBy: Created by.
        createdAt: Created at.
        uses: Uses.
    """

    available: int
    code: str
    createdAt: str
    createdBy: str
    disabled: bool
    forAccount: str
    uses: List['models.ComAtprotoServerDefs.InviteCodeUse']


@dataclass
class InviteCodeUse(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.defs`.

    Attributes:
        usedBy: Used by.
        usedAt: Used at.
    """

    usedAt: str
    usedBy: str
