##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.actor.getStatus`."""

    can_create_groups: bool  #: Whether the viewer's account is allowed to create group chats. New accounts are restricted from creating groups.
    chat_disabled: bool  #: True when the viewer's account is disabled and cannot actively participate in chat.
    group_member_limit: int  #: The maximum number of members allowed in a group conversation.
