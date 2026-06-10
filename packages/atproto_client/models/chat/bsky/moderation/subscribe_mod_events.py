#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`chat.bsky.moderation.subscribeModEvents`."""

    cursor: t.Optional[str] = (
        None  #: The last known event seq number to backfill from. Use '2222222222222' to backfill from the beginning. Don't specify a cursor to listen only for new events.
    )


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[
        t.Optional[str]
    ]  #: The last known event seq number to backfill from. Use '2222222222222' to backfill from the beginning. Don't specify a cursor to listen only for new events.


class EventConvoFirstMessage(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when the first message was sent on a convo."""

    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    recipients: t.List[
        string_formats.Did
    ]  #: The list of DIDs message recipients. Does not include the sender, which is in the `user` field.
    rev: str  #: Rev.
    user: string_formats.Did  #: The DID of the message author.
    message_id: t.Optional[str] = None  #: Message id.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventConvoFirstMessage'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventConvoFirstMessage', alias='$type', frozen=True
    )


class EventGroupChatCreated(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fire when a group chat is created."""

    actor_did: string_formats.Did  #: The DID of the actor performing the action. For this event, same as ownerDid.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: The name set at creation time.
    initial_member_dids: t.List[string_formats.Did]  #: DIDs of everyone added at creation time.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatCreated'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatCreated', alias='$type', frozen=True
    )


class EventGroupChatMemberAdded(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a member is added to a group chat. Note that members are added in the 'request' state."""

    actor_did: string_formats.Did  #: The DID of the actor performing the action. For this event, same as ownerDid.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    request_members_count: int  #: The number of members who have not yet accepted the convo.
    rev: str  #: Rev.
    subject_did: string_formats.Did  #: The DID of the member who was added.
    subject_follows_owner: bool  #: Whether the added member follows the group owner.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberAdded'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberAdded', alias='$type', frozen=True
    )


class EventGroupChatMemberJoined(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a member joins a group chat via an join link that does not require approval."""

    actor_did: string_formats.Did  #: The DID of the person joining.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    join_link_code: str  #: The code of the join link used to join.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    subject_follows_owner: bool  #: Whether the joining member follows the group owner.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberJoined'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberJoined', alias='$type', frozen=True
    )


class EventGroupChatJoinRequest(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a user requests to join a group chat via an join link that requires approval."""

    actor_did: string_formats.Did  #: The DID of the person requesting to join.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    join_link_code: str  #: The code of the join link used to request joining.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    subject_follows_owner: bool  #: Whether the requesting member follows the group owner.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequest'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequest', alias='$type', frozen=True
    )


class EventGroupChatJoinRequestApproved(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a join request is approved by the group owner."""

    actor_did: string_formats.Did  #: The DID of the owner approving the request.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    subject_did: string_formats.Did  #: The DID of the member whose request was approved.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequestApproved'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequestApproved', alias='$type', frozen=True
    )


class EventGroupChatJoinRequestRejected(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a join request is rejected by the group owner."""

    actor_did: string_formats.Did  #: The DID of the owner rejecting the request.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    subject_did: string_formats.Did  #: The DID of the member whose request was rejected.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequestRejected'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatJoinRequestRejected', alias='$type', frozen=True
    )


class EventChatAccepted(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a user accepts a chat convo, either explicitly or by sending a message."""

    actor_did: string_formats.Did  #: The DID of the person accepting the convo.
    convo_created_at: string_formats.DateTime  #: When the convo was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    method: t.Union[t.Literal['explicit'], t.Literal['message'], str]  #: How the convo was accepted.
    rev: str  #: Rev.
    group_member_count: t.Optional[int] = (
        None  #: Current member count at the time of the event. Only present for group convos.
    )
    group_name: t.Optional[str] = None  #: The name of the group chat. Only present for group convos.
    owner_did: t.Optional[string_formats.Did] = None  #: The DID of the group chat owner. Only present for group convos.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventChatAccepted'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventChatAccepted', alias='$type', frozen=True
    )


class EventGroupChatMemberLeft(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a member leaves or is removed from a group chat."""

    actor_did: string_formats.Did  #: The DID of the actor. For voluntary: the person leaving. For kicked: the owner.
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Group name.
    leave_method: t.Union[t.Literal['voluntary'], t.Literal['kicked'], str]  #: How the member left.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    subject_did: string_formats.Did  #: The DID of the member who left or was removed.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberLeft'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatMemberLeft', alias='$type', frozen=True
    )


class EventGroupChatUpdated(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a group chat's metadata or status changes."""

    actor_did: string_formats.Did  #: The DID of the actor performing the action (the owner).
    convo_created_at: string_formats.DateTime  #: When the group was originally created.
    convo_id: str  #: Convo id.
    created_at: string_formats.DateTime  #: Created at.
    group_member_count: int  #: Current member count at the time of the event.
    group_name: str  #: Current group name.
    owner_did: string_formats.Did  #: The DID of the group chat owner.
    rev: str  #: Rev.
    update_type: t.Union[
        t.Literal['name_changed'],
        t.Literal['locked'],
        t.Literal['locked_permanently'],
        t.Literal['unlocked'],
        t.Literal['join_link_created'],
        t.Literal['join_link_disabled'],
        t.Literal['join_link_settings_changed'],
        str,
    ]  #: What changed.
    join_link_code: t.Optional[str] = (
        None  #: The code of the join link. Only present when updateType is join-link-related.
    )
    join_link_followers_only: t.Optional[bool] = (
        None  #: Whether the join link is restricted to followers of the owner. Only present when updateType is join-link-related.
    )
    join_link_requires_approval: t.Optional[bool] = (
        None  #: Whether the join link requires owner approval to join. Only present when updateType is join-link-related.
    )
    lock_reason: t.Optional[
        t.Union[
            t.Literal['owner_action'],
            t.Literal['owner_left'],
            t.Literal['owner_deactivated'],
            t.Literal['owner_deleted'],
            t.Literal['owner_suspended'],
            t.Literal['owner_taken_down'],
            t.Literal['label_applied'],
            t.Literal['convo_taken_down'],
            str,
        ]
    ] = None  #: Why the group was locked. Only present when updateType is 'locked'.
    new_name: t.Optional[str] = None  #: The new group name. Only present when updateType is 'name_changed'.
    old_name: t.Optional[str] = None  #: The previous group name. Only present when updateType is 'name_changed'.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventGroupChatUpdated'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventGroupChatUpdated', alias='$type', frozen=True
    )


class EventRateLimitExceeded(base.ModelBase):
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`. Fired when a user exceeds a rate limit."""

    actor_did: string_formats.Did  #: The DID of the user who hit the rate limit.
    created_at: string_formats.DateTime  #: Created at.
    endpoint: str  #: The NSID of the endpoint that was rate limited.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.moderation.subscribeModEvents#eventRateLimitExceeded'] = Field(
        default='chat.bsky.moderation.subscribeModEvents#eventRateLimitExceeded', alias='$type', frozen=True
    )
