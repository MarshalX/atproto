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

    """Input data model for :obj:`com.atproto.server.createSession`.

    Attributes:
        identifier: Handle or other identifier supported by the server for the authenticating user.
        password: Password.
    """

    identifier: str
    password: str


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createSession`.

    Attributes:
        accessJwt: Access jwt.
        refreshJwt: Refresh jwt.
        handle: Handle.
        did: Did.
        email: Email.
    """

    accessJwt: str
    did: str
    handle: str
    refreshJwt: str
    email: Optional[str] = None
