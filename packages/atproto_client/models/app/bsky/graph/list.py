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
    """Record model for :obj:`app.bsky.graph.list`."""

    created_at: str  #: Created at.
    name: str = Field(min_length=1, max_length=64)  #: Display name for list; can not be empty.
    purpose: (
        'models.AppBskyGraphDefs.ListPurpose'
    )  #: Defines the purpose of the list (aka, moderation-oriented or curration-oriented).
    avatar: t.Optional['BlobRef'] = None  #: Avatar.
    description: t.Optional[str] = Field(default=None, max_length=3000)  #: Description.
    description_facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None  #: Description facets.
    labels: t.Optional[
        te.Annotated[t.Union['models.ComAtprotoLabelDefs.SelfLabels'], Field(default=None, discriminator='py_type')]
    ] = None  #: Labels.

    py_type: te.Literal['app.bsky.graph.list'] = Field(default='app.bsky.graph.list', alias='$type', frozen=True)


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
    """Get record response for :obj:`models.AppBskyGraphList.Record`."""

    uri: str  #: The URI of the record.
    value: 'models.AppBskyGraphList.Record'  #: The record.
    cid: t.Optional[str] = None  #: The CID of the record.


class ListRecordsResponse(base.SugarResponseModelBase):
    """List records response for :obj:`models.AppBskyGraphList.Record`."""

    records: t.Dict[str, 'models.AppBskyGraphList.Record']  #: Map of URIs to records.
    cursor: t.Optional[str] = None  #: Next page cursor.


class CreateRecordResponse(base.SugarResponseModelBase):
    """Create record response for :obj:`models.AppBskyGraphList.Record`."""

    uri: str  #: The URI of the record.
    cid: str  #: The CID of the record.
