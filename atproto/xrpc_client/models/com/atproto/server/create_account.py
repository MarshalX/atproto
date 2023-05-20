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

    """Input data model for :obj:`com.atproto.server.createAccount`.

    Attributes:
        email: Email.
        handle: Handle.
        did: Did.
        inviteCode: Invite code.
        password: Password.
        recoveryKey: Recovery key.
    """

    email: str
    handle: str
    password: str
    did: t.Optional[str] = None
    inviteCode: t.Optional[str] = None
    recoveryKey: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createAccount`.

    Attributes:
        accessJwt: Access jwt.
        refreshJwt: Refresh jwt.
        handle: Handle.
        did: Did.
    """

    accessJwt: str
    did: str
    handle: str
    refreshJwt: str
