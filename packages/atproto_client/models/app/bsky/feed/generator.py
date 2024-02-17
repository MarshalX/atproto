##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class Record(base.RecordModelBase):
    """Record model for :obj:`app.bsky.feed.generator`."""

    created_at: str  #: Created at.
    did: str  #: Did.
    display_name: str = Field(max_length=240)  #: Display name.
    avatar: t.Optional['BlobRef'] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(default=None, discriminator='py_type')]
    ] = None  #: Self-label values.

    py_type: te.Literal['app.bsky.feed.generator'] = Field(
        default='app.bsky.feed.generator', alias='$type', frozen=True
    )


class Main(Record):
    def __init_subclass__(cls, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**data)

    def __init__(self, **data: t.Any) -> None:
        import warnings

        warnings.warn('Main class is deprecated. Use Record class instead.', DeprecationWarning, stacklevel=2)
        super().__init__(**data)


class GetRecordResponse(base.SugarResponseModelBase):
    """Get record response for :obj:`models.AppBskyFeedGenerator.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyFeedGenerator.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyFeedGenerator.Record`."""

    records: t.Dict[str, 'models.AppBskyFeedGenerator.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyFeedGenerator.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
