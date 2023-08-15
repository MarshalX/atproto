##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.getSession`."""

    did: str  #: Did.
    handle: str  #: Handle.
    email: t.Optional[str] = None  #: Email.
