##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.refreshSession`."""

    access_jwt: str  #: Access jwt.
    did: str  #: Did.
    handle: str  #: Handle.
    refresh_jwt: str  #: Refresh jwt.
    did_doc: t.Optional['UnknownType'] = None  #: Did doc.
