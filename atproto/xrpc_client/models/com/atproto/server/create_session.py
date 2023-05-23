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

    """Input data model for :obj:`com.atproto.server.createSession`."""

    identifier: str  #: Handle or other identifier supported by the server for the authenticating user.
    password: str  #: Password.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createSession`."""

    accessJwt: str  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refreshJwt: str  #: Refresh jwt.
    email: t.Optional[str] = None  #: Email.
