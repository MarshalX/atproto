#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base

LinkEnabledStatus = t.Union[t.Literal['enabled'], t.Literal['disabled'], str]  #: Link enabled status

JoinRule = t.Union[t.Literal['anyone'], t.Literal['followedByOwner'], str]  #: Join rule


class JoinLinkView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. Join link view to be used within a group view, so the convo is surrounding, not specified inside this view."""

    code: str  #: Code.
    created_at: string_formats.DateTime  #: Created at.
    enabled_status: 'models.ChatBskyGroupDefs.LinkEnabledStatus'  #: Enabled status.
    join_rule: 'models.ChatBskyGroupDefs.JoinRule'  #: Join rule.
    require_approval: bool  #: Require approval.

    py_type: t.Literal['chat.bsky.group.defs#joinLinkView'] = Field(
        default='chat.bsky.group.defs#joinLinkView', alias='$type', frozen=True
    )


class JoinLinkPreviewView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. Preview that can be shown in feeds, including to unauthenticated viewers."""

    code: str  #: Code.
    convo_id: str  #: Convo id.
    join_rule: 'models.ChatBskyGroupDefs.JoinRule'  #: Join rule.
    member_count: int  #: Member count.
    member_limit: int  #: Member limit.
    name: str  #: Name.
    owner: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Owner.
    require_approval: bool  #: Require approval.
    convo: t.Optional['models.ChatBskyConvoDefs.ConvoView'] = (
        None  #: Present only if the request is authenticated and the user is a member of the group.
    )
    viewer: t.Optional['models.ChatBskyGroupDefs.JoinLinkViewerState'] = None  #: Viewer.

    py_type: t.Literal['chat.bsky.group.defs#joinLinkPreviewView'] = Field(
        default='chat.bsky.group.defs#joinLinkPreviewView', alias='$type', frozen=True
    )


class DisabledJoinLinkPreviewView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. Preview for a disabled join link. Carries only the code so clients can correlate with the input and render a disabled state."""

    code: str  #: Code.

    py_type: t.Literal['chat.bsky.group.defs#disabledJoinLinkPreviewView'] = Field(
        default='chat.bsky.group.defs#disabledJoinLinkPreviewView', alias='$type', frozen=True
    )


class InvalidJoinLinkPreviewView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. Preview for a join link code that does not map to an existing link. Carries only the code so clients can correlate with the input and render an invalid state."""

    code: str  #: Code.

    py_type: t.Literal['chat.bsky.group.defs#invalidJoinLinkPreviewView'] = Field(
        default='chat.bsky.group.defs#invalidJoinLinkPreviewView', alias='$type', frozen=True
    )


class JoinLinkViewerState(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`."""

    requested_at: t.Optional[string_formats.DateTime] = None  #: Requested at.

    py_type: t.Literal['chat.bsky.group.defs#joinLinkViewerState'] = Field(
        default='chat.bsky.group.defs#joinLinkViewerState', alias='$type', frozen=True
    )


class JoinRequestView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. A join request from the perspective of the group owner."""

    convo_id: str  #: Convo id.
    requested_at: string_formats.DateTime  #: Requested at.
    requested_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Requested by.

    py_type: t.Literal['chat.bsky.group.defs#joinRequestView'] = Field(
        default='chat.bsky.group.defs#joinRequestView', alias='$type', frozen=True
    )


class JoinRequestConvoView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.group.defs`. A join request from the perspective of the requester, including enough group context to render the request in a list (e.g. group name, owner, member count)."""

    convo_id: str  #: Convo id.
    member_count: int  #: Member count.
    member_limit: int  #: Member limit.
    name: str  #: Name.
    owner: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Owner.
    viewer: 'models.ChatBskyGroupDefs.JoinLinkViewerState'  #: Viewer.

    py_type: t.Literal['chat.bsky.group.defs#joinRequestConvoView'] = Field(
        default='chat.bsky.group.defs#joinRequestConvoView', alias='$type', frozen=True
    )
