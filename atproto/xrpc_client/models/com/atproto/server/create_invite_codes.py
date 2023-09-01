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


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createInviteCodes`."""

    codeCount: int  #: Code count.
    useCount: int  #: Use count.
    forAccounts: t.Optional[t.List[str]] = None  #: For accounts.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createInviteCodes`."""

    codes: t.List['models.ComAtprotoServerCreateInviteCodes.AccountCodes']  #: Codes.


class AccountCodes(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.createInviteCodes`."""

    account: str  #: Account.
    codes: t.List[str]  #: Codes.

    py_type: te.Literal['com.atproto.server.createInviteCodes#accountCodes'] = Field(
        default='com.atproto.server.createInviteCodes#accountCodes', alias='$type', frozen=True
    )
