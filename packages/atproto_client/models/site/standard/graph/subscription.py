##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`site.standard.graph.subscription`."""

    publication: string_formats.AtUri  #: AT-URI reference to the publication record being subscribed to (ex: at://did:plc:abc123/site.standard.publication/xyz789).
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.

    py_type: t.Literal['site.standard.graph.subscription'] = Field(
        default='site.standard.graph.subscription', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SiteStandardGraphSubscription.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SiteStandardGraphSubscription.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SiteStandardGraphSubscription.Record`."""

    records: t.Dict[str, 'models.SiteStandardGraphSubscription.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SiteStandardGraphSubscription.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
