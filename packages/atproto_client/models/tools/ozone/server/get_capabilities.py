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


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.server.getCapabilities`."""

    notifications: t.Optional['models.ToolsOzoneServerGetCapabilities.NotificationConfig'] = None  #: Notifications.


class NotificationConfig(base.ModelBase):
    """Definition model for :obj:`tools.ozone.server.getCapabilities`."""

    channels: t.List[t.Union[t.Literal['inApp', 'push'], str]] = Field(min_length=1)  #: Channels.

    py_type: t.Literal['tools.ozone.server.getCapabilities#notificationConfig'] = Field(
        default='tools.ozone.server.getCapabilities#notificationConfig', alias='$type', frozen=True
    )
