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

    """Input data model for :obj:`com.atproto.server.createSession`."""

    identifier: str  #: Handle or other identifier supported by the server for the authenticating user.
    password: str  #: Password.


class DataDict(te.TypedDict):
    identifier: str  #: Handle or other identifier supported by the server for the authenticating user.
    password: str  #: Password.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.createSession`."""

    access_jwt: str = Field(alias='accessJwt')  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refresh_jwt: str = Field(alias='refreshJwt')  #: Refresh jwt.
    did_doc: t.Optional['UnknownType'] = Field(default=None, alias='didDoc')  #: Did doc.
    email: t.Optional[str] = None  #: Email.
    email_confirmed: t.Optional[bool] = Field(default=None, alias='emailConfirmed')  #: Email confirmed.
