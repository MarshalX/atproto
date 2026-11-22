#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base, unknown_union


class Record(base.RecordModelBase):
    """Record model for :obj:`com.atproto.space.policy`."""

    policy: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoPersonalspacePolicy.Main',
            'models.ComAtprotoMemberspacePolicy.Main',
            'models.ComAtprotoManagedspacePolicy.Main',
        ]
    ]  #: PDSes must support all of the listed policies. Other space hosts may support only some of them, and any host may support policies beyond those listed.

    py_type: t.Literal['com.atproto.space.policy'] = Field(
        default='com.atproto.space.policy', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.ComAtprotoSpacePolicy.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.ComAtprotoSpacePolicy.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.ComAtprotoSpacePolicy.Record`."""

    records: t.Dict[str, 'models.ComAtprotoSpacePolicy.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.ComAtprotoSpacePolicy.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
