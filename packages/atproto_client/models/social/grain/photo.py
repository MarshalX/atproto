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
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`social.grain.photo`."""

    photo: 'BlobRef'  #: Photo.
    alt: t.Optional[str] = None  #: Alt text description of the image, for accessibility.
    aspect_ratio: t.Optional['models.SocialGrainDefs.AspectRatio'] = None  #: Aspect ratio.
    created_at: t.Optional[string_formats.DateTime] = None  #: Created at.

    py_type: t.Literal['social.grain.photo'] = Field(default='social.grain.photo', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SocialGrainPhoto.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SocialGrainPhoto.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SocialGrainPhoto.Record`."""

    records: t.Dict[str, 'models.SocialGrainPhoto.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SocialGrainPhoto.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
