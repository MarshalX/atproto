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
    """Input data model for :obj:`chat.bsky.notification.putPreferences`."""

    chat: t.Optional['models.ChatBskyNotificationDefs.ChatPreference'] = None  #: Chat.
    chat_request: t.Optional['models.ChatBskyNotificationDefs.ChatPreference'] = None  #: Chat request.


class DataDict(t.TypedDict):
    chat: te.NotRequired[t.Optional['models.ChatBskyNotificationDefs.ChatPreference']]  #: Chat.
    chat_request: te.NotRequired[t.Optional['models.ChatBskyNotificationDefs.ChatPreference']]  #: Chat request.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.notification.putPreferences`."""

    preferences: 'models.ChatBskyNotificationDefs.Preferences'  #: Preferences.
