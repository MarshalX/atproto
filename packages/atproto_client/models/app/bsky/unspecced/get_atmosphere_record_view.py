#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereRecordView`."""

    uri: string_formats.AtUri  #: Complete DID-based AT-URI of the record, including collection and record key.
    cid: t.Optional[string_formats.Cid] = None  #: Optional CID pinning the exact record version at `uri`.


class ParamsDict(t.TypedDict):
    uri: string_formats.AtUri  #: Complete DID-based AT-URI of the record, including collection and record key.
    cid: te.NotRequired[t.Optional[string_formats.Cid]]  #: Optional CID pinning the exact record version at `uri`.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereRecordView`."""

    associated_records: t.Optional[t.List['UnknownType']] = (
        None  #: Associated records. The raw record data, index-aligned with `associatedRefs`.
    )
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (URI+CID) of the record itself, followed by the dependency records selected for its collection (a document's publication; a gallery's items and photos). Index-aligned with `associatedRecords`.
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
    ] = None  #: Hydrated view of the record. Present only when the records supply enough information to populate the required fields.
