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
from atproto_client.models import base, unknown_union


class Record(base.RecordModelBase):
    """Record model for :obj:`social.grain.gallery`."""

    created_at: string_formats.DateTime  #: Created at.
    title: str = Field(max_length=100)  #: Title.
    description: te.Annotated[t.Optional[str], Field(max_length=1000)] = None  #: Description.
    labels: t.Optional[unknown_union.OpenUnion['models.ComAtprotoLabelDefs.SelfLabels']] = (
        None  #: Self-label values for this post. Effectively content warnings.
    )

    py_type: t.Literal['social.grain.gallery'] = Field(default='social.grain.gallery', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SocialGrainGallery.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SocialGrainGallery.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SocialGrainGallery.Record`."""

    records: t.Dict[str, 'models.SocialGrainGallery.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SocialGrainGallery.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
