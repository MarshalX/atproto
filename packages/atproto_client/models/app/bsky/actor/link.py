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
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base, unknown_union


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.actor.link`."""

    created_at: string_formats.DateTime  #: Created at.
    url: string_formats.Uri  #: The link destination, an https URL.
    icon: t.Optional['BlobRef'] = None  #: The destination site's icon, uploaded when the link is saved.
    labels: t.Optional[unknown_union.OpenUnion['models.ComAtprotoLabelDefs.SelfLabels']] = (
        None  #: Self-label values for this link.
    )
    title: te.Annotated[t.Optional[str], Field(max_length=320)] = (
        None  #: Optional label for the link. Clients can fall back to the destination's domain.
    )

    py_type: t.Literal['app.bsky.actor.link'] = Field(default='app.bsky.actor.link', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.AppBskyActorLink.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyActorLink.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyActorLink.Record`."""

    records: t.Dict[str, 'models.AppBskyActorLink.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyActorLink.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
