##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.notification.getUnreadCount`."""

    seen_at: t.Optional[str] = Field(default=None, alias='seenAt')  #: Seen at.


class ParamsDict(te.TypedDict):
    seen_at: te.NotRequired[t.Optional[str]]  #: Seen at.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.getUnreadCount`."""

    count: int  #: Count.
