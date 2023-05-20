##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.disableInviteCodes`.

    Attributes:
        codes: Codes.
        accounts: Accounts.
    """

    accounts: t.Optional[t.List[str]] = None
    codes: t.Optional[t.List[str]] = None
