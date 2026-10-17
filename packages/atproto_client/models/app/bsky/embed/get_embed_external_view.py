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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.embed.getEmbedExternalView`."""

    url: string_formats.Uri  #: The canonical web URL the embed represents (typically the URL the user pasted into the composer). Used as the returned view's `uri`, and validated against the resolved records.
    canonical_uri: t.Optional[string_formats.AtUri] = (
        None  #: The canonical AT URI of the atproto record found on the webpage. When provided, takes precedence over `uris`, which is then ignored.
    )
    uris: te.Annotated[t.Optional[t.List[string_formats.AtUri]], Field(max_length=4)] = (
        None  #: Legacy input for Standard.site callers, ignored when `canonicalUri` is provided. A single record is selected from it: the first site.standard.document URI, otherwise the first site.standard.publication URI. Other entries are ignored; a document's publication is discovered from the document itself.
    )


class ParamsDict(t.TypedDict):
    url: string_formats.Uri  #: The canonical web URL the embed represents (typically the URL the user pasted into the composer). Used as the returned view's `uri`, and validated against the resolved records.
    canonical_uri: te.NotRequired[
        t.Optional[string_formats.AtUri]
    ]  #: The canonical AT URI of the atproto record found on the webpage. When provided, takes precedence over `uris`, which is then ignored.
    uris: te.NotRequired[
        t.Optional[t.List[string_formats.AtUri]]
    ]  #: Legacy input for Standard.site callers, ignored when `canonicalUri` is provided. A single record is selected from it: the first site.standard.document URI, otherwise the first site.standard.publication URI. Other entries are ignored; a document's publication is discovered from the document itself.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.embed.getEmbedExternalView`."""

    associated_records: t.Optional[t.List['UnknownType']] = (
        None  #: Associated records. The raw record data of the Atmosphere records selected for persistence, index-aligned with `associatedRefs`. Returned for convenience, to avoid the client separately fetching them. Present only when validation passed.
    )
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (URI+CID) of the Atmosphere records selected for persistence in a post, suitable for embedding into its external.associatedRefs: the canonical record, plus only the additional records the service chooses to persist for its collection. This can be a subset of the records used to render `data`, which may also draw on other hydrated records such as recommendations, subscriptions, or favorites. Present only when validation passed. Index-aligned with `associatedRecords`.
    )
    data: t.Optional[
        unknown_union.OpenUnion[
            t.Union[
                'models.AppBskyEmbedExternal.ViewArticle',
                'models.AppBskyEmbedExternal.ViewArticlePublication',
                'models.AppBskyEmbedExternal.ViewGallery',
                'models.AppBskyEmbedExternal.ViewLivestream',
            ]
        ]
    ] = None  #: Preferred to #view. Hydrated data of the embed. Present only when validation passed and the records supply enough information to populate the required fields.
    unverified_associated_records: t.Optional[t.List['UnknownType']] = (
        None  #: Unverified associated records. The raw record data of the persistence-selected Atmosphere records, index-aligned with `unverifiedAssociatedRefs`. Present only when validation failed.
    )
    unverified_associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (URI+CID) of the same persistence-selected Atmosphere records (the canonical record plus chosen additional records) when validation of the requested `url` failed. These must not be written to a post. Index-aligned with `unverifiedAssociatedRecords`.
    )
    view: t.Optional['models.AppBskyEmbedExternal.View'] = (
        None  #: Legacy hydrated view of the embed, returned for Standard.site records only. Present only when validation passed and the records supply enough information to populate the required `viewExternal` fields.
    )
