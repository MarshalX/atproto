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


class Preferences(base.ModelBase):
    """Definition model for :obj:`chat.bsky.notification.defs`."""

    chat: 'models.ChatBskyNotificationDefs.ChatPreference'  #: Chat.
    chat_request: 'models.ChatBskyNotificationDefs.ChatPreference'  #: Chat request.

    py_type: t.Literal['chat.bsky.notification.defs#preferences'] = Field(
        default='chat.bsky.notification.defs#preferences', alias='$type', frozen=True
    )


class ChatPreference(base.ModelBase):
    """Definition model for :obj:`chat.bsky.notification.defs`."""

    include: t.Union[t.Literal['all'], t.Literal['follows'], str]  #: Include.
    push: bool  #: Push.

    py_type: t.Literal['chat.bsky.notification.defs#chatPreference'] = Field(
        default='chat.bsky.notification.defs#chatPreference', alias='$type', frozen=True
    )
