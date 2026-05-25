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


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`chat.bsky.moderation.getMessageContext`."""

    message_id: str  #: Message id.
    after: t.Optional[int] = (
        5  #: Number of user messages after the target to include. System messages between the target and the latest returned user message are also included, capped per gap by `maxInterleavedSystemMessages`. If there are no user messages after the target, up to `maxInterleavedSystemMessages` system messages immediately following the target are returned instead.
    )
    before: t.Optional[int] = (
        5  #: Number of user messages before the target to include. System messages between the earliest returned user message and the target are also included, capped per gap by `maxInterleavedSystemMessages`. If there are no user messages before the target, up to `maxInterleavedSystemMessages` system messages immediately preceding the target are returned instead.
    )
    convo_id: t.Optional[str] = (
        None  #: Conversation that the message is from. NOTE: this field will eventually be required.
    )
    max_interleaved_system_messages: te.Annotated[t.Optional[int], Field(ge=0, le=1000)] = (
        None  #: Maximum number of system messages to include per gap between consecutive returned messages (and per side when there are no user messages on that side). Within a gap, the system messages closest to the earlier message are kept.
    )


class ParamsDict(t.TypedDict):
    message_id: str  #: Message id.
    after: te.NotRequired[
        t.Optional[int]
    ]  #: Number of user messages after the target to include. System messages between the target and the latest returned user message are also included, capped per gap by `maxInterleavedSystemMessages`. If there are no user messages after the target, up to `maxInterleavedSystemMessages` system messages immediately following the target are returned instead.
    before: te.NotRequired[
        t.Optional[int]
    ]  #: Number of user messages before the target to include. System messages between the earliest returned user message and the target are also included, capped per gap by `maxInterleavedSystemMessages`. If there are no user messages before the target, up to `maxInterleavedSystemMessages` system messages immediately preceding the target are returned instead.
    convo_id: te.NotRequired[
        t.Optional[str]
    ]  #: Conversation that the message is from. NOTE: this field will eventually be required.
    max_interleaved_system_messages: te.NotRequired[
        t.Optional[int]
    ]  #: Maximum number of system messages to include per gap between consecutive returned messages (and per side when there are no user messages on that side). Within a gap, the system messages closest to the earlier message are kept.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.moderation.getMessageContext`."""

    messages: t.List[
        te.Annotated[
            t.Union['models.ChatBskyConvoDefs.MessageView', 'models.ChatBskyConvoDefs.SystemMessageView'],
            Field(discriminator='py_type'),
        ]
    ]  #: Messages.
