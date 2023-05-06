##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.refreshSession`.

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
