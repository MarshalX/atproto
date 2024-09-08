##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.notification.getUnreadCount`."""

    priority: t.Optional[bool] = None  #: Priority.
    seen_at: t.Optional[str] = None  #: Seen at.


class ParamsDict(t.TypedDict):
    priority: te.NotRequired[t.Optional[bool]]  #: Priority.
    seen_at: te.NotRequired[t.Optional[str]]  #: Seen at.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.notification.getUnreadCount`."""

    count: int  #: Count.
