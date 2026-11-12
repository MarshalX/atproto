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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.unspecced.getAtmosphereRecordViews`."""

    records: t.List['models.AppBskyUnspeccedGetAtmosphereRecordViews.RecordRef'] = Field(
        min_length=1, max_length=25
    )  #: Records to fetch. Results preserve this order, including duplicates.


class DataDict(t.TypedDict):
    records: t.List[
        'models.AppBskyUnspeccedGetAtmosphereRecordViews.RecordRef'
    ]  #: Records to fetch. Results preserve this order, including duplicates.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereRecordViews`."""

    views: t.List['models.AppBskyUnspeccedGetAtmosphereRecordViews.RecordView'] = Field(
        max_length=25
    )  #: Index-aligned with the input records. Missing or invisible roots produce empty objects. Visible roots without a supported view still return raw associations. Each result includes only its own dependencies.


class RecordRef(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereRecordViews`."""

    uri: string_formats.AtUri  #: Complete DID-based AT-URI of the record, including collection and record key.
    cid: t.Optional[string_formats.Cid] = (
        None  #: Optional CID pinning the exact record version. Omit to fetch the latest version. Unavailable pins never fall back to latest.
    )

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereRecordViews#recordRef'] = Field(
        default='app.bsky.unspecced.getAtmosphereRecordViews#recordRef', alias='$type', frozen=True
    )


class RecordView(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereRecordViews`."""

    associated_records: t.Optional[t.List['UnknownType']] = None  #: Raw record data, index-aligned with associatedRefs.
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: The selected root followed by its visible latest dependencies: a document's publication or a gallery's items and photos. Index-aligned with associatedRecords.
    )
    view: t.Optional[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyEmbedExternal.ViewArticle',
                'models.AppBskyEmbedExternal.ViewArticlePublication',
                'models.AppBskyEmbedExternal.ViewGallery',
                'models.AppBskyEmbedExternal.ViewLivestream',
            ]
        ]
    ] = None  #: Hydrated view, present only when the records supply enough information to populate the required fields.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereRecordViews#recordView'] = Field(
        default='app.bsky.unspecced.getAtmosphereRecordViews#recordView', alias='$type', frozen=True
    )
