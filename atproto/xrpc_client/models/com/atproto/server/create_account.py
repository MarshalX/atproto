##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAccount`."""

    email: str  #: Email.
    handle: str  #: Handle.
    password: str  #: Password.
    did: t.Optional[str] = None  #: Did.
    invite_code: t.Optional[str] = Field(default=None, alias='inviteCode')  #: Invite code.
    plc_op: t.Optional[t.Union[str, bytes]] = Field(default=None, alias='plcOp')  #: Plc op.
    recovery_key: t.Optional[str] = Field(default=None, alias='recoveryKey')  #: Recovery key.


class DataDict(te.TypedDict):
    email: str  #: Email.
    handle: str  #: Handle.
    password: str  #: Password.
    did: te.NotRequired[t.Optional[str]]  #: Did.
    invite_code: te.NotRequired[t.Optional[str]]  #: Invite code.
    plc_op: te.NotRequired[t.Optional[t.Union[str, bytes]]]  #: Plc op.
    recovery_key: te.NotRequired[t.Optional[str]]  #: Recovery key.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createAccount`."""

    access_jwt: str = Field(alias='accessJwt')  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refresh_jwt: str = Field(alias='refreshJwt')  #: Refresh jwt.
    did_doc: t.Optional['UnknownType'] = Field(default=None, alias='didDoc')  #: Did doc.
