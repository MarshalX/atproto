#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.inbox.claimPushNotifications`."""

    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.


class DataDict(t.TypedDict):
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.claimPushNotifications`."""

    expired: int = Field(ge=0, le=100)  #: Expired.
    notifications: t.List['models.ToolsOzoneInboxClaimPushNotifications.Item']  #: Notifications.
    processed: int = Field(ge=0, le=100)  #: Processed.
    suppressed: int = Field(ge=0, le=100)  #: Suppressed.


class Item(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.claimPushNotifications`."""

    category: t.Union[t.Literal['reports', 'account', 'labels'], str]  #: Category.
    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Id.
    lease_token: str  #: Lease token.
    reason: str  #: Reason.
    recipient_did: string_formats.Did  #: Recipient did.
    target: unknown_union.OpenUnion[
        t.Union[
            'models.ToolsOzoneInboxDefs.ReportRef',
            'models.ToolsOzoneInboxDefs.SubjectRef',
            'models.ToolsOzoneInboxDefs.StandingRef',
        ]
    ]  #: Target.

    py_type: t.Literal['tools.ozone.inbox.claimPushNotifications#item'] = Field(
        default='tools.ozone.inbox.claimPushNotifications#item', alias='$type', frozen=True
    )
