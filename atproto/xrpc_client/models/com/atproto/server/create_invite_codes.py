##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createInviteCodes`.

    Attributes:
        codeCount: Code count.
        useCount: Use count.
        forAccounts: For accounts.
    """

    codeCount: int
    useCount: int
    forAccounts: Optional[List[str]] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createInviteCodes`.

    Attributes:
        codes: Codes.
    """

    codes: List['models.ComAtprotoServerCreateInviteCodes.AccountCodes']


@dataclass
class AccountCodes(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.createInviteCodes`.

    Attributes:
        account: Account.
        codes: Codes.
    """

    account: str
    codes: List[str]
