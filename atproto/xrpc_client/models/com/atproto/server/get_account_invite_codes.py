##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.server.getAccountInviteCodes`."""

    create_available: t.Optional[bool] = Field(default=True, alias='createAvailable')  #: Create available.
    include_used: t.Optional[bool] = Field(default=True, alias='includeUsed')  #: Include used.


class ParamsDict(te.TypedDict):
    create_available: te.NotRequired[t.Optional[bool]]  #: Create available.
    include_used: te.NotRequired[t.Optional[bool]]  #: Include used.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.server.getAccountInviteCodes`."""

    codes: t.List['models.ComAtprotoServerDefs.InviteCode']  #: Codes.
