#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.inbox.ackPushNotifications`."""

    items: t.List['models.ToolsOzoneInboxAckPushNotifications.Item'] = Field(min_length=1, max_length=100)  #: Items.


class DataDict(t.TypedDict):
    items: t.List['models.ToolsOzoneInboxAckPushNotifications.Item']  #: Items.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.ackPushNotifications`."""

    acknowledged: t.List[int]  #: Acknowledged.


class Item(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.ackPushNotifications`."""

    id: int  #: Id.
    lease_token: str = Field(max_length=64)  #: Lease token.

    py_type: t.Literal['tools.ozone.inbox.ackPushNotifications#item'] = Field(
        default='tools.ozone.inbox.ackPushNotifications#item', alias='$type', frozen=True
    )
