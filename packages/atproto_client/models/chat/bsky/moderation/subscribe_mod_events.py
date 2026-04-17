##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


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
    """Definition model for :obj:`chat.bsky.moderation.subscribeModEvents`."""

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
