#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.actor.contentVisibilityDeclaration`."""

    hide_from_algorithmic_recommendations: bool  #: Whether the account requests that its posts be hidden from algorithmic recommendations. Consumers must treat a missing record as false.

    py_type: t.Literal['app.bsky.actor.contentVisibilityDeclaration'] = Field(
        default='app.bsky.actor.contentVisibilityDeclaration', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.AppBskyActorContentVisibilityDeclaration.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyActorContentVisibilityDeclaration.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyActorContentVisibilityDeclaration.Record`."""

    records: t.Dict[str, 'models.AppBskyActorContentVisibilityDeclaration.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyActorContentVisibilityDeclaration.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
