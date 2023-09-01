##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class InviteCode(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.defs`."""

    available: int  #: Available.
    code: str  #: Code.
    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    disabled: bool  #: Disabled.
    forAccount: str  #: For account.
    uses: t.List['models.ComAtprotoServerDefs.InviteCodeUse']  #: Uses.

    py_type: te.Literal['com.atproto.server.defs#inviteCode'] = Field(
        default='com.atproto.server.defs#inviteCode', alias='$type', frozen=True
    )


class InviteCodeUse(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.defs`."""

    usedAt: str  #: Used at.
    usedBy: str  #: Used by.

    py_type: te.Literal['com.atproto.server.defs#inviteCodeUse'] = Field(
        default='com.atproto.server.defs#inviteCodeUse', alias='$type', frozen=True
    )
