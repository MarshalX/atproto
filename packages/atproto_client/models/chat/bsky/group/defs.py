##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base

LinkEnabledStatus = t.Union[t.Literal['enabled'], t.Literal['disabled'], str]  #: Link enabled status

JoinRule = t.Union[t.Literal['anyone'], t.Literal['followedByOwner'], str]  #: Join rule


class JoinLinkView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`."""

    code: str  #: Code.
    created_at: string_formats.DateTime  #: Created at.
    enabled_status: 'models.ChatBskyGroupDefs.LinkEnabledStatus'  #: Enabled status.
    join_rule: 'models.ChatBskyGroupDefs.JoinRule'  #: Join rule.
    require_approval: bool  #: Require approval.

    py_type: t.Literal['chat.bsky.group.defs#joinLinkView'] = Field(
        default='chat.bsky.group.defs#joinLinkView', alias='$type', frozen=True
    )


class GroupPublicView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`."""

    member_count: int  #: Member count.
    name: str  #: Name.
    owner: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Owner.
    require_approval: bool  #: Require approval.

    py_type: t.Literal['chat.bsky.group.defs#groupPublicView'] = Field(
        default='chat.bsky.group.defs#groupPublicView', alias='$type', frozen=True
    )


class JoinRequestView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`."""

    convo_id: str  #: Convo id.
    requested_at: string_formats.DateTime  #: Requested at.
    requested_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Requested by.

    py_type: t.Literal['chat.bsky.group.defs#joinRequestView'] = Field(
        default='chat.bsky.group.defs#joinRequestView', alias='$type', frozen=True
    )
