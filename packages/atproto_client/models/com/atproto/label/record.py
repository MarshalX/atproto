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
    """Record model for :obj:`com.atproto.label.record`."""

    cts: string_formats.DateTime  #: Timestamp when this label was created.
    uri: string_formats.Uri  #: URI of the record, repository (account), or other resource that this label applies to. Currently only intended for use in the context of atproto spaces.
    val: str = Field(max_length=128)  #: The short string name of the value or type of this label.
    cid: t.Optional[string_formats.Cid] = (
        None  #: Optionally, CID specifying the specific version of 'uri' resource this label applies to.
    )
    exp: t.Optional[string_formats.DateTime] = None  #: Timestamp at which this label expires (no longer applies).

    py_type: t.Literal['com.atproto.label.record'] = Field(
        default='com.atproto.label.record', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.ComAtprotoLabelRecord.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.ComAtprotoLabelRecord.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.ComAtprotoLabelRecord.Record`."""

    records: t.Dict[str, 'models.ComAtprotoLabelRecord.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.ComAtprotoLabelRecord.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
