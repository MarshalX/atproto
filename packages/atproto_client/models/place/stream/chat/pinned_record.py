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


class Record(base.RecordModelBase):
    """Record model for :obj:`place.stream.chat.pinnedRecord`."""

    created_at: string_formats.DateTime  #: When this pin was created.
    pinned_message: string_formats.AtUri  #: AT-URI of the pinned chat message.
    expires_at: t.Optional[string_formats.DateTime] = (
        None  #: Optional expiration time. If set, the pin is considered inactive after this time.
    )
    pinned_by: t.Optional[string_formats.Did] = None  #: DID of the user who pinned the message.

    py_type: t.Literal['place.stream.chat.pinnedRecord'] = Field(
        default='place.stream.chat.pinnedRecord', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.PlaceStreamChatPinnedRecord.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.PlaceStreamChatPinnedRecord.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.PlaceStreamChatPinnedRecord.Record`."""

    records: t.Dict[str, 'models.PlaceStreamChatPinnedRecord.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.PlaceStreamChatPinnedRecord.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
