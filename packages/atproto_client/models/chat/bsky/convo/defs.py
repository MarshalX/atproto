##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class MessageRef(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    convo_id: str  #: Convo id.
    did: str  #: Did.
    message_id: str  #: Message id.

    py_type: t.Literal['chat.bsky.convo.defs#messageRef'] = Field(
        default='chat.bsky.convo.defs#messageRef', alias='$type', frozen=True
    )


class MessageInput(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    text: str = Field(max_length=10000)  #: Text.
    embed: t.Optional[
        te.Annotated[t.Union['models.AppBskyEmbedRecord.Main'], Field(default=None, discriminator='py_type')]
    ] = None  #: Embed.
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
    sent_at: str  #: Sent at.
    text: str = Field(max_length=10000)  #: Text.
    embed: t.Optional[
        te.Annotated[t.Union['models.AppBskyEmbedRecord.View'], Field(default=None, discriminator='py_type')]
    ] = None  #: Embed.
    facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = (
        None  #: Annotations of text (mentions, URLs, hashtags, etc).
    )

    py_type: t.Literal['chat.bsky.convo.defs#messageView'] = Field(
        default='chat.bsky.convo.defs#messageView', alias='$type', frozen=True
    )


class DeletedMessageView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    id: str  #: Id.
    rev: str  #: Rev.
    sender: 'models.ChatBskyConvoDefs.MessageViewSender'  #: Sender.
    sent_at: str  #: Sent at.

    py_type: t.Literal['chat.bsky.convo.defs#deletedMessageView'] = Field(
        default='chat.bsky.convo.defs#deletedMessageView', alias='$type', frozen=True
    )


class MessageViewSender(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    did: str  #: Did.

    py_type: t.Literal['chat.bsky.convo.defs#messageViewSender'] = Field(
        default='chat.bsky.convo.defs#messageViewSender', alias='$type', frozen=True
    )


class ConvoView(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    id: str  #: Id.
    members: t.List['models.ChatBskyActorDefs.ProfileViewBasic']  #: Members.
    muted: bool  #: Muted.
    rev: str  #: Rev.
    unread_count: int  #: Unread count.
    last_message: t.Optional[
        te.Annotated[
            t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Last message.

    py_type: t.Literal['chat.bsky.convo.defs#convoView'] = Field(
        default='chat.bsky.convo.defs#convoView', alias='$type', frozen=True
    )


class LogBeginConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logBeginConvo'] = Field(
        default='chat.bsky.convo.defs#logBeginConvo', alias='$type', frozen=True
    )


class LogLeaveConvo(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    convo_id: str  #: Convo id.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logLeaveConvo'] = Field(
        default='chat.bsky.convo.defs#logLeaveConvo', alias='$type', frozen=True
    )


class LogCreateMessage(base.ModelBase):
    """Definition model for :obj:`chat.bsky.convo.defs`."""

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
    """Definition model for :obj:`chat.bsky.convo.defs`."""

    convo_id: str  #: Convo id.
    message: te.Annotated[
        t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.DeletedMessageView'],
        Field(discriminator='py_type'),
    ]  #: Message.
    rev: str  #: Rev.

    py_type: t.Literal['chat.bsky.convo.defs#logDeleteMessage'] = Field(
        default='chat.bsky.convo.defs#logDeleteMessage', alias='$type', frozen=True
    )
