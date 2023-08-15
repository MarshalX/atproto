##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAccount`."""

    email: str  #: Email.
    handle: str  #: Handle.
    password: str  #: Password.
    did: t.Optional[str] = None  #: Did.
    inviteCode: t.Optional[str] = None  #: Invite code.
    recoveryKey: t.Optional[str] = None  #: Recovery key.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createAccount`."""

    accessJwt: str  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refreshJwt: str  #: Refresh jwt.
