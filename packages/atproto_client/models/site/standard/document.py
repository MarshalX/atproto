##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class Contributor(base.ModelBase):
    """Definition model for :obj:`site.standard.document`."""

    did: string_formats.Did  #: Did.
    display_name: te.Annotated[t.Optional[str], Field(max_length=1000)] = None  #: Display name.
    role: te.Annotated[t.Optional[str], Field(max_length=1000)] = None  #: Role.

    py_type: t.Literal['site.standard.document#contributor'] = Field(
        default='site.standard.document#contributor', alias='$type', frozen=True
    )


class Record(base.RecordModelBase):
    """Record model for :obj:`site.standard.document`."""

    published_at: string_formats.DateTime  #: Timestamp of the documents publish time.
    site: string_formats.Uri  #: Points to a publication record (at://) or a publication url (https://) for loose documents. Avoid trailing slashes.
    title: str = Field(max_length=5000)  #: Title of the document.
    bsky_post_ref: t.Optional['models.ComAtprotoRepoStrongRef.Main'] = (
        None  #: Strong reference to a Bluesky post. Useful to keep track of comments off-platform.
    )
    content: t.Optional[te.Annotated[t.Union['base.UnknownUnionModel'], Field()]] = (
        None  #: Open union used to define the record's content. Each entry must specify a $type and may be extended with other lexicons to support additional content formats.
    )
    contributors: t.Optional[t.List['models.SiteStandardDocument.Contributor']] = None  #: Contributors.
    cover_image: t.Optional['BlobRef'] = None  #: Image to used for thumbnail or cover image. Less than 1MB is size.
    description: te.Annotated[t.Optional[str], Field(max_length=30000)] = (
        None  #: A brief description or excerpt from the document.
    )
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(discriminator='py_type')]
    ] = None  #: Self-label values for this post. Effectively content warnings.
    links: t.Optional[te.Annotated[t.Union['base.UnknownUnionModel'], Field()]] = (
        None  #: Array of values describing relationships between this document and external resources.
    )
    path: t.Optional[str] = (
        None  #: Combine with site or publication url to construct a canonical URL to the document. Prepend with a leading slash.
    )
    tags: t.Optional[t.List[str]] = (
        None  #: Array of strings used to tag or categorize the document. Avoid prepending tags with hashtags.
    )
    text_content: t.Optional[str] = (
        None  #: Plaintext representation of the documents contents. Should not contain markdown or other formatting.
    )
    updated_at: t.Optional[string_formats.DateTime] = None  #: Timestamp of the documents last edit.

    py_type: t.Literal['site.standard.document'] = Field(default='site.standard.document', alias='$type', frozen=True)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.SiteStandardDocument.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.SiteStandardDocument.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.SiteStandardDocument.Record`."""

    records: t.Dict[str, 'models.SiteStandardDocument.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.SiteStandardDocument.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
