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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class MessageView(base.ModelBase):
    """Definition model for :obj:`place.stream.chat.defs`."""

    author: 'models.AppBskyActorDefs.ProfileViewBasic'  #: Author.
    cid: string_formats.Cid  #: Cid.
    indexed_at: string_formats.DateTime  #: Indexed at.
    record: 'UnknownType'  #: Record.
    uri: string_formats.AtUri  #: Uri.
    badges: te.Annotated[t.Optional[t.List['models.PlaceStreamBadgeDefs.BadgeView']], Field(max_length=3)] = (
        None  #: Up to 3 badge tokens to display with the message. First badge is server-controlled, remaining badges are user-settable. Tokens are looked up in badges.json for display info.
    )
    chat_profile: t.Optional['models.PlaceStreamChatProfile.Record'] = None  #: Chat profile.
    deleted: t.Optional[bool] = (
        None  #: If true, this message has been deleted or labeled and should be cleared from the cache.
    )
    reply_to: t.Optional[unknown_union.OpenUnion['models.PlaceStreamChatDefs.MessageView']] = None  #: Reply to.

    py_type: t.Literal['place.stream.chat.defs#messageView'] = Field(
        default='place.stream.chat.defs#messageView', alias='$type', frozen=True
    )


class PinnedRecordView(base.ModelBase):
    """Definition model for :obj:`place.stream.chat.defs`. View of a pinned chat record with hydrated message data."""

    cid: string_formats.Cid  #: Cid.
    indexed_at: string_formats.DateTime  #: Indexed at.
    record: 'models.PlaceStreamChatPinnedRecord.Record'  #: Record.
    uri: string_formats.AtUri  #: Uri.
    message: t.Optional['models.PlaceStreamChatDefs.MessageView'] = None  #: Message.
    pinned_by: t.Optional['models.PlaceStreamChatProfile.Record'] = None  #: Pinned by.

    py_type: t.Literal['place.stream.chat.defs#pinnedRecordView'] = Field(
        default='place.stream.chat.defs#pinnedRecordView', alias='$type', frozen=True
    )
