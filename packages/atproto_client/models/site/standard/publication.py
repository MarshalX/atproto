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
from atproto_client.models import base


class Preferences(base.ModelBase):
    """Definition model for :obj:`site.standard.publication`."""

    show_in_discover: t.Optional[bool] = (
        True  #: Boolean which decides whether the publication should appear in discovery feeds.
    )

    py_type: t.Literal['site.standard.publication#preferences'] = Field(
        default='site.standard.publication#preferences', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`site.standard.publication`."""

    name: str = Field(max_length=5000)  #: Name of the publication.
    url: string_formats.Uri  #: Base publication url (ex: https://standard.site). The canonical document URL is formed by combining this value with the document path.
    basic_theme: t.Optional['models.SiteStandardThemeBasic.Record'] = (
        None  #: Simplified publication theme for tools and apps to utilize when displaying content.
    )
    description: te.Annotated[t.Optional[str], Field(max_length=30000)] = None  #: Brief description of the publication.
    icon: t.Optional['BlobRef'] = None  #: Square image to identify the publication. Should be at least 256x256.
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(discriminator='py_type')]
    ] = None  #: Self-label values for this publication. Effectively content warnings.
    preferences: t.Optional['models.SiteStandardPublication.Preferences'] = (
        None  #: Object containing platform specific preferences (with a few shared properties).
    )

    py_type: t.Literal['site.standard.publication'] = Field(
        default='site.standard.publication', alias='$type', frozen=True
    )


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SiteStandardPublication.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SiteStandardPublication.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SiteStandardPublication.Record`."""

    records: t.Dict[str, 'models.SiteStandardPublication.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SiteStandardPublication.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
