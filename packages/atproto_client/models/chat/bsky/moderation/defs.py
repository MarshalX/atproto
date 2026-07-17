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
from atproto_client.models import base


class ConvoView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.defs`. A view of a conversation for moderation purposes. Unlike chat.bsky.convo.defs#convoView, it does not include viewer-specific data (such as muted, unreadCount, status, lastMessage, lastReaction), since the requester is a moderator and not a member of the conversation. The member list is not included; use chat.bsky.moderation.getConvoMembers to list members."""

    id: str  #: Id.
    rev: str  #: Rev.
    kind: t.Optional[
        te.Annotated[
            t.Union['models.ChatBskyModerationDefs.DirectConvo', 'models.ChatBskyModerationDefs.GroupConvo'],
            Field(discriminator='py_type'),
        ]
    ] = None  #: Union field that has data specific to different kinds of convos.

    py_type: t.Literal['chat.bsky.moderation.defs#convoView'] = Field(
        default='chat.bsky.moderation.defs#convoView', alias='$type', frozen=True
    )


class DirectConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.defs`. Data specific to a direct conversation, for moderation purposes."""

    py_type: t.Literal['chat.bsky.moderation.defs#directConvo'] = Field(
        default='chat.bsky.moderation.defs#directConvo', alias='$type', frozen=True
    )


class GroupConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.defs`. Data specific to a group conversation, for moderation purposes. Unlike chat.bsky.convo.defs#groupConvo, it does not include viewer-specific data (such as unreadJoinRequestCount), since the requester is a moderator and not a member of the conversation."""

    created_at: string_formats.DateTime  #: Created at.
    join_request_count: int  #: The total number of pending join requests for the group conversation. This information is only visible to the owner and to moderators. Capped at 21.
    lock_status: 'models.ChatBskyConvoDefs.ConvoLockStatus'  #: The lock status of the conversation.
    member_count: int  #: The total number of members in the group conversation.
    member_limit: int  #: The maximum number of members allowed in the group conversation.
    name: str = Field(max_length=500)  #: The display name of the group conversation.
    join_link: t.Optional['models.ChatBskyGroupDefs.JoinLinkView'] = None  #: Join link.

    py_type: t.Literal['chat.bsky.moderation.defs#groupConvo'] = Field(
        default='chat.bsky.moderation.defs#groupConvo', alias='$type', frozen=True
    )
