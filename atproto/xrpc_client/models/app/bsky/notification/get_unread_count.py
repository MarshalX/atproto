##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.notification.getUnreadCount`."""

    seen_at: t.Optional[str] = Field(default=None, alias='seenAt')  #: Seen at.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.getUnreadCount`."""

    count: int  #: Count.
