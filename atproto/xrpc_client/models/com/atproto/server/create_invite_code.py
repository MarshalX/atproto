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

    """Input data model for :obj:`com.atproto.server.createInviteCode`."""

    useCount: int  #: Use count.
    forAccount: t.Optional[str] = None  #: For account.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createInviteCode`."""

    code: str  #: Code.
