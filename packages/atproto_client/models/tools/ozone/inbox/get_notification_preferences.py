#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.getNotificationPreferences`."""

    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    )


class ParamsDict(t.TypedDict):
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.getNotificationPreferences`."""

    preferences: 'models.ToolsOzoneInboxDefs.NotificationPreferences'  #: Preferences.
