##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.identity.resolveHandle`."""

    handle: t.Optional[str] = None  #: The handle to resolve. If not supplied, will resolve the host's own handle.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.identity.resolveHandle`."""

    did: str  #: Did.
