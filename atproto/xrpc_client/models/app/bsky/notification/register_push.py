##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`app.bsky.notification.registerPush`."""

    app_id: str = Field(alias='appId')  #: App id.
    platform: str  #: Platform.
    service_did: str = Field(alias='serviceDid')  #: Service did.
    token: str  #: Token.


class DataDict(te.TypedDict):
    app_id: str  #: App id.
    platform: str  #: Platform.
    service_did: str  #: Service did.
    token: str  #: Token.
