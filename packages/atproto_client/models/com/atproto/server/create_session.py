##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.server.createSession`."""

    identifier: str  #: Handle or other identifier supported by the server for the authenticating user.
    password: str  #: Password.


class DataDict(te.TypedDict):
    identifier: str  #: Handle or other identifier supported by the server for the authenticating user.
    password: str  #: Password.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.createSession`."""

    access_jwt: str  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refresh_jwt: str  #: Refresh jwt.
    did_doc: t.Optional['UnknownType'] = None  #: Did doc.
    email: t.Optional[str] = None  #: Email.
    email_confirmed: t.Optional[bool] = None  #: Email confirmed.
