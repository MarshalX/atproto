##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.unknown_type import UnknownInputType
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.temp.transferAccount`."""

    did: str  #: Did.
    handle: str  #: Handle.
    plc_op: 'UnknownInputType' = Field(alias='plcOp')  #: Plc op.


class DataDict(te.TypedDict):
    did: str  #: Did.
    handle: str  #: Handle.
    plc_op: 'UnknownInputType'  #: Plc op.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.temp.transferAccount`."""

    access_jwt: str = Field(alias='accessJwt')  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refresh_jwt: str = Field(alias='refreshJwt')  #: Refresh jwt.
