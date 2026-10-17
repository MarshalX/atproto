#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.inbox.putNotificationPreferences`."""

    account: t.Optional[bool] = (
        None  #: Notify about moderation actions against the account or its content, excluding labeling.
    )
    labels: t.Optional[bool] = None  #: Notify about labels applied to or removed from the account or its content.
    reports: t.Optional[bool] = None  #: Notify about outcomes of reports filed by the account.


class DataDict(t.TypedDict):
    account: te.NotRequired[
        t.Optional[bool]
    ]  #: Notify about moderation actions against the account or its content, excluding labeling.
    labels: te.NotRequired[
        t.Optional[bool]
    ]  #: Notify about labels applied to or removed from the account or its content.
    reports: te.NotRequired[t.Optional[bool]]  #: Notify about outcomes of reports filed by the account.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.putNotificationPreferences`."""

    preferences: 'models.ToolsOzoneInboxDefs.NotificationPreferences'  #: Preferences.
