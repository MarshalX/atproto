##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.server.getServiceAuth`."""

    aud: str  #: The DID of the service that the token will be used to authenticate with.


class ParamsDict(t.TypedDict):
    aud: str  #: The DID of the service that the token will be used to authenticate with.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.getServiceAuth`."""

    token: str  #: Token.
