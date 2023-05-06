##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Optional

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAccount`.

    Attributes:
        email: Email.
        handle: Handle.
        inviteCode: Invite code.
        password: Password.
        recoveryKey: Recovery key.
    """

    email: str
    handle: str
    password: str
    inviteCode: Optional[str] = None
    recoveryKey: Optional[str] = None


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
