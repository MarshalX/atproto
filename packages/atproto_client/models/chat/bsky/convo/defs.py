##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base

ConvoKind = t.Union[t.Literal['direct'], t.Literal['group'], str]  #: Convo kind

ConvoLockStatus = t.Union[
    t.Literal['unlocked'], t.Literal['locked'], t.Literal['locked-permanently'], str
]  #: Convo lock status

ConvoStatus = t.Union[t.Literal['request'], t.Literal['accepted'], str]  #: Convo status


class MessageRef(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    convo_id: str  #: Convo id.
    did: string_formats.Did  #: Did.
    message_id: str  #: Message id.

    py_type: t.Literal['chat.bsky.convo.defs#messageRef'] = Field(
        default='chat.bsky.convo.defs#messageRef', alias='$type', frozen=True
    )


class MessageInput(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    text: str = Field(max_length=10000)  #: Text.
    embed: t.Optional[te.Annotated[t.Union['models.AppBskyEmbedRecord.Main'], Field(discriminator='py_type')]] = (
        None  #: Embed.
    )
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = (
        None  #: Annotations of text (mentions, URLs, hashtags, etc).
    )

    py_type: t.Literal['chat.bsky.convo.defs#messageInput'] = Field(
        default='chat.bsky.convo.defs#messageInput', alias='$type', frozen=True
    )


class MessageView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    id: str  #: Id.
    rev: str  #: Rev.
    sender: 'models.ChatBskyConvoDefs.MessageViewSender'  #: Sender.
    sent_at: string_formats.DateTime  #: Sent at.
    text: str = Field(max_length=10000)  #: Text.
    embed: t.Optional[te.Annotated[t.Union['models.AppBskyEmbedRecord.View'], Field(discriminator='py_type')]] = (
        None  #: Embed.
    )
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = (
        None  #: Annotations of text (mentions, URLs, hashtags, etc).
    )
    reactions: t.Optional[t.List['models.ChatBskyConvoDefs.ReactionView']] = (
        None  #: Reactions to this message, in ascending order of creation time.
    )

    py_type: t.Literal['chat.bsky.convo.defs#messageView'] = Field(
        default='chat.bsky.convo.defs#messageView', alias='$type', frozen=True
    )


class SystemMessageView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]."""

    data: te.Annotated[
        t.Union[
            'models.ChatBskyConvoDefs.SystemMessageDataAddMember',
            'models.ChatBskyConvoDefs.SystemMessageDataRemoveMember',
            'models.ChatBskyConvoDefs.SystemMessageDataMemberJoin',
            'models.ChatBskyConvoDefs.SystemMessageDataMemberLeave',
            'models.ChatBskyConvoDefs.SystemMessageDataLockConvo',
            'models.ChatBskyConvoDefs.SystemMessageDataUnlockConvo',
            'models.ChatBskyConvoDefs.SystemMessageDataLockConvoPermanently',
            'models.ChatBskyConvoDefs.SystemMessageDataEditGroup',
            'models.ChatBskyConvoDefs.SystemMessageDataCreateJoinLink',
            'models.ChatBskyConvoDefs.SystemMessageDataEditJoinLink',
            'models.ChatBskyConvoDefs.SystemMessageDataEnableJoinLink',
            'models.ChatBskyConvoDefs.SystemMessageDataDisableJoinLink',
        ],
        Field(discriminator='py_type'),
    ]  #: Data.
    id: str  #: Id.
    rev: str  #: Rev.
    sent_at: string_formats.DateTime  #: Sent at.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageView'] = Field(
        default='chat.bsky.convo.defs#systemMessageView', alias='$type', frozen=True
    )


class SystemMessageDataAddMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating a user was added to the group convo."""

    added_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Added by.
    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who was added.
    role: 'models.ChatBskyActorDefs.MemberRole'  #: Role the user was added to the group with. The role from 'member' will reflect the current data, not historical.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataAddMember'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataAddMember', alias='$type', frozen=True
    )


class SystemMessageDataRemoveMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating a user was removed from the group convo."""

    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who was removed.
    removed_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Removed by.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataRemoveMember'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataRemoveMember', alias='$type', frozen=True
    )


class SystemMessageDataMemberJoin(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating a user joined the group convo via join link."""

    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who joined.
    role: 'models.ChatBskyActorDefs.MemberRole'  #: Role the user was added to the group with. The role from 'member' will reflect the current data, not historical.
    approved_by: t.Optional['models.ChatBskyActorDefs.ProfileViewBasic'] = (
        None  #: If join link was configured to require approval, this will be set to who approved the request. Undefined if approval was not required.
    )

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataMemberJoin'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataMemberJoin', alias='$type', frozen=True
    )


class SystemMessageDataMemberLeave(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating a user voluntarily left the group convo."""

    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who left the group.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataMemberLeave'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataMemberLeave', alias='$type', frozen=True
    )


class SystemMessageDataLockConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group convo was locked."""

    locked_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who locked the group.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataLockConvo'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataLockConvo', alias='$type', frozen=True
    )


class SystemMessageDataUnlockConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group convo was unlocked."""

    unlocked_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who unlocked the group.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataUnlockConvo'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataUnlockConvo', alias='$type', frozen=True
    )


class SystemMessageDataLockConvoPermanently(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group convo was locked permanently."""

    locked_by: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Current view of the member who locked the group.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataLockConvoPermanently'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataLockConvoPermanently', alias='$type', frozen=True
    )


class SystemMessageDataEditGroup(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group info was edited."""

    new_name: t.Optional[str] = None  #: Group name that replaced the old.
    old_name: t.Optional[str] = None  #: Group name that was replaced.

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataEditGroup'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataEditGroup', alias='$type', frozen=True
    )


class SystemMessageDataCreateJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group join link was created."""

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataCreateJoinLink'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataCreateJoinLink', alias='$type', frozen=True
    )


class SystemMessageDataEditJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group join link was edited."""

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataEditJoinLink'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataEditJoinLink', alias='$type', frozen=True
    )


class SystemMessageDataEnableJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group join link was enabled."""

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataEnableJoinLink'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataEnableJoinLink', alias='$type', frozen=True
    )


class SystemMessageDataDisableJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. System message indicating the group join link was disabled."""

    py_type: t.Literal['chat.bsky.convo.defs#systemMessageDataDisableJoinLink'] = Field(
        default='chat.bsky.convo.defs#systemMessageDataDisableJoinLink', alias='$type', frozen=True
    )


class DeletedMessageView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    id: str  #: Id.
    rev: str  #: Rev.
    sender: 'models.ChatBskyConvoDefs.MessageViewSender'  #: Sender.
    sent_at: string_formats.DateTime  #: Sent at.

    py_type: t.Literal['chat.bsky.convo.defs#deletedMessageView'] = Field(
        default='chat.bsky.convo.defs#deletedMessageView', alias='$type', frozen=True
    )


class MessageViewSender(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    did: string_formats.Did  #: Did.

    py_type: t.Literal['chat.bsky.convo.defs#messageViewSender'] = Field(
        default='chat.bsky.convo.defs#messageViewSender', alias='$type', frozen=True
    )


class ReactionView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    created_at: string_formats.DateTime  #: Created at.
    sender: 'models.ChatBskyConvoDefs.ReactionViewSender'  #: Sender.
    value: str  #: Value.

    py_type: t.Literal['chat.bsky.convo.defs#reactionView'] = Field(
        default='chat.bsky.convo.defs#reactionView', alias='$type', frozen=True
    )


class ReactionViewSender(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    did: string_formats.Did  #: Did.

    py_type: t.Literal['chat.bsky.convo.defs#reactionViewSender'] = Field(
        default='chat.bsky.convo.defs#reactionViewSender', alias='$type', frozen=True
    )


class MessageAndReactionView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    message: 'models.ChatBskyConvoDefs.MessageView'  #: Message.
    reaction: 'models.ChatBskyConvoDefs.ReactionView'  #: Reaction.

    py_type: t.Literal['chat.bsky.convo.defs#messageAndReactionView'] = Field(
        default='chat.bsky.convo.defs#messageAndReactionView', alias='$type', frozen=True
    )


class ConvoView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    id: str  #: Id.
    members: t.List[
        'models.ChatBskyActorDefs.ProfileViewBasic'
    ]  #: Members of this conversation. For direct convos, it will be an immutable list of the 2 members. For group convos, it will a list of important members (the first few members, the viewer, the member who invited the viewer, the member who sent the last message, the member who sent the last reaction), but will not contain the full list of members. NOTE: TBD an endpoint to list all members.
    muted: bool  #: Muted.
    rev: str  #: Rev.
    unread_count: int  #: Unread count.
    kind: t.Optional[
        te.Annotated[
            t.Union['models.ChatBskyConvoDefs.DirectConvo', 'models.ChatBskyConvoDefs.GroupConvo'],
            Field(discriminator='py_type'),
        ]
    ] = None  #: Union field that has data specific to different kinds of convos.
    last_message: t.Optional[
        te.Annotated[
            t.Union[
                'models.ChatBskyConvoDefs.MessageView',
                'models.ChatBskyConvoDefs.DeletedMessageView',
                'models.ChatBskyConvoDefs.SystemMessageView',
            ],
            Field(discriminator='py_type'),
        ]
    ] = None  #: Last message.
    last_reaction: t.Optional[
        te.Annotated[t.Union['models.ChatBskyConvoDefs.MessageAndReactionView'], Field(discriminator='py_type')]
    ] = None  #: Last reaction.
    status: t.Optional['models.ChatBskyConvoDefs.ConvoStatus'] = (
        None  #: Convo status for the viewer member (not the convo itself).
    )

    py_type: t.Literal['chat.bsky.convo.defs#convoView'] = Field(
        default='chat.bsky.convo.defs#convoView', alias='$type', frozen=True
    )


class DirectConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]."""

    py_type: t.Literal['chat.bsky.convo.defs#directConvo'] = Field(
        default='chat.bsky.convo.defs#directConvo', alias='$type', frozen=True
    )


class GroupConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]."""

    lock_status: 'models.ChatBskyConvoDefs.ConvoLockStatus'  #: The lock status of the conversation.
    name: str = Field(max_length=1280)  #: The display name of the group conversation.
    join_link: t.Optional['models.ChatBskyGroupDefs.JoinLinkView'] = None  #: Join link.

    py_type: t.Literal['chat.bsky.convo.defs#groupConvo'] = Field(
        default='chat.bsky.convo.defs#groupConvo', alias='$type', frozen=True
    )


class LogBeginConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating a convo containing the viewer was started. Can be direct or group. When a member is added to a group convo, they also get this event."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logBeginConvo'] = Field(
        default='chat.bsky.convo.defs#logBeginConvo', alias='$type', frozen=True
    )


class LogAcceptConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating the viewer accepted a convo, and it can be moved out of the request inbox. Can be direct or group."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logAcceptConvo'] = Field(
        default='chat.bsky.convo.defs#logAcceptConvo', alias='$type', frozen=True
    )


class LogLeaveConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating the viewer left a convo. Can be direct or group."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logLeaveConvo'] = Field(
        default='chat.bsky.convo.defs#logLeaveConvo', alias='$type', frozen=True
    )


class LogMuteConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating the viewer muted a convo. Can be direct or group."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logMuteConvo'] = Field(
        default='chat.bsky.convo.defs#logMuteConvo', alias='$type', frozen=True
    )


class LogUnmuteConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating the viewer unmuted a convo. Can be direct or group."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logUnmuteConvo'] = Field(
        default='chat.bsky.convo.defs#logUnmuteConvo', alias='$type', frozen=True
    )


class LogCreateMessage(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating a user-originated message was created. Is not emitted for system messages."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
        Field(discriminator='py_type'),
    ]  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logCreateMessage'] = Field(
        default='chat.bsky.convo.defs#logCreateMessage', alias='$type', frozen=True
    )


class LogDeleteMessage(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating a user-originated message was deleted. Is not emitted for system messages."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
        Field(discriminator='py_type'),
    ]  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logDeleteMessage'] = Field(
        default='chat.bsky.convo.defs#logDeleteMessage', alias='$type', frozen=True
    )


class LogReadMessage(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. DEPRECATED: use logReadConvo instead. Event indicating a convo was read up to a certain message."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union[
            'models.ChatBskyConvoDefs.MessageView',
            'models.ChatBskyConvoDefs.DeletedMessageView',
            'models.ChatBskyConvoDefs.SystemMessageView',
        ],
        Field(discriminator='py_type'),
    ]  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logReadMessage'] = Field(
        default='chat.bsky.convo.defs#logReadMessage', alias='$type', frozen=True
    )


class LogAddReaction(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating a reaction was added to a message."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
        Field(discriminator='py_type'),
    ]  #: Message.
    reaction: 'models.ChatBskyConvoDefs.ReactionView'  #: Reaction.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logAddReaction'] = Field(
        default='chat.bsky.convo.defs#logAddReaction', alias='$type', frozen=True
    )


class LogRemoveReaction(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. Event indicating a reaction was removed from a message."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
        Field(discriminator='py_type'),
    ]  #: Message.
    reaction: 'models.ChatBskyConvoDefs.ReactionView'  #: Reaction.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logRemoveReaction'] = Field(
        default='chat.bsky.convo.defs#logRemoveReaction', alias='$type', frozen=True
    )


class LogReadConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a convo was read up to a certain message."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union[
            'models.ChatBskyConvoDefs.MessageView',
            'models.ChatBskyConvoDefs.DeletedMessageView',
            'models.ChatBskyConvoDefs.SystemMessageView',
        ],
        Field(discriminator='py_type'),
    ]  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logReadConvo'] = Field(
        default='chat.bsky.convo.defs#logReadConvo', alias='$type', frozen=True
    )


class LogAddMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a member was added to a group convo. The member who was added gets a logBeginConvo (to create the convo) but also a logAddMember (to show the system message as the first message the user sees)."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataAddMember'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logAddMember'] = Field(
        default='chat.bsky.convo.defs#logAddMember', alias='$type', frozen=True
    )


class LogRemoveMember(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a member was removed from a group convo. The member who was removed gets a logLeaveConvo (to leave the convo) but not a logRemoveMember (because they already left, so can't see the system message)."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataRemoveMember'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logRemoveMember'] = Field(
        default='chat.bsky.convo.defs#logRemoveMember', alias='$type', frozen=True
    )


class LogMemberJoin(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a member joined a group convo via join link. The member who was added gets a logBeginConvo (to create the convo) but also a logMemberJoin (to show the system message as the first message the user sees)."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataMemberJoin'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logMemberJoin'] = Field(
        default='chat.bsky.convo.defs#logMemberJoin', alias='$type', frozen=True
    )


class LogMemberLeave(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a member voluntarily left a group convo. The member who was removed gets a logLeaveConvo (to leave the convo) but not a logMemberLeave (because they already left, so can't see the system message)."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataMemberLeave'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logMemberLeave'] = Field(
        default='chat.bsky.convo.defs#logMemberLeave', alias='$type', frozen=True
    )


class LogLockConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a group convo was locked."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataLockConvo'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logLockConvo'] = Field(
        default='chat.bsky.convo.defs#logLockConvo', alias='$type', frozen=True
    )


class LogUnlockConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a group convo was unlocked."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataUnlockConvo'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logUnlockConvo'] = Field(
        default='chat.bsky.convo.defs#logUnlockConvo', alias='$type', frozen=True
    )


class LogLockConvoPermanently(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a group convo was locked permanently."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataLockConvoPermanently'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logLockConvoPermanently'] = Field(
        default='chat.bsky.convo.defs#logLockConvoPermanently', alias='$type', frozen=True
    )


class LogEditGroup(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating info about group convo was edited."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataEditGroup'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logEditGroup'] = Field(
        default='chat.bsky.convo.defs#logEditGroup', alias='$type', frozen=True
    )


class LogCreateJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join link was created for a group convo."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataCreateJoinLink'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logCreateJoinLink'] = Field(
        default='chat.bsky.convo.defs#logCreateJoinLink', alias='$type', frozen=True
    )


class LogEditJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a settings about a join link for a group convo were edited."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataEditJoinLink'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logEditJoinLink'] = Field(
        default='chat.bsky.convo.defs#logEditJoinLink', alias='$type', frozen=True
    )


class LogEnableJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join link was enabled for a group convo."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataEnableJoinLink'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logEnableJoinLink'] = Field(
        default='chat.bsky.convo.defs#logEnableJoinLink', alias='$type', frozen=True
    )


class LogDisableJoinLink(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join link was disabled for a group convo."""

    convo_id: str  #: Convo id.
    message: 'models.ChatBskyConvoDefs.SystemMessageDataDisableJoinLink'  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logDisableJoinLink'] = Field(
        default='chat.bsky.convo.defs#logDisableJoinLink', alias='$type', frozen=True
    )


class LogIncomingJoinRequest(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join request was made to a group the viewer owns. Only the owner gets this."""

    convo_id: str  #: Convo id.
    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Prospective member who requested to join.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logIncomingJoinRequest'] = Field(
        default='chat.bsky.convo.defs#logIncomingJoinRequest', alias='$type', frozen=True
    )


class LogApproveJoinRequest(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join request was approved by the viewer. Only the owner gets this. The approved member gets a logBeginConvo."""

    convo_id: str  #: Convo id.
    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Prospective member who requested to join.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logApproveJoinRequest'] = Field(
        default='chat.bsky.convo.defs#logApproveJoinRequest', alias='$type', frozen=True
    )


class LogRejectJoinRequest(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join request was rejected by the viewer. Only the owner gets this."""

    convo_id: str  #: Convo id.
    member: 'models.ChatBskyActorDefs.ProfileViewBasic'  #: Prospective member who requested to join.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logRejectJoinRequest'] = Field(
        default='chat.bsky.convo.defs#logRejectJoinRequest', alias='$type', frozen=True
    )


class LogOutgoingJoinRequest(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`. [NOTE: This is under active development and should be considered unstable while this note is here]. Event indicating a join request was made by the viewer."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logOutgoingJoinRequest'] = Field(
        default='chat.bsky.convo.defs#logOutgoingJoinRequest', alias='$type', frozen=True
    )
