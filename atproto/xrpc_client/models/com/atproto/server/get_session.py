##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.getSession`."""

    did: str  #: Did.
    handle: str  #: Handle.
    did_doc: t.Optional['UnknownType'] = Field(default=None, alias='didDoc')  #: Did doc.
    email: t.Optional[str] = None  #: Email.
    email_confirmed: t.Optional[bool] = Field(default=None, alias='emailConfirmed')  #: Email confirmed.
