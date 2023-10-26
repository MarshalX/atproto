##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createInviteCode`."""

    use_count: int = Field(alias='useCount')  #: Use count.
    for_account: t.Optional[str] = Field(default=None, alias='forAccount')  #: For account.


class DataDict(te.TypedDict):
    use_count: int  #: Use count.
    for_account: te.NotRequired[t.Optional[str]]  #: For account.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createInviteCode`."""

    code: str  #: Code.
