##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.embed.getEmbedExternalView`."""

    uris: t.List[string_formats.AtUri] = Field(
        max_length=4
    )  #: AT-URIs of any Atmosphere records that can be resolved and used to construct #externalView views. Example: a site.standard.document and optionally its associated site.standard.publication.
    url: string_formats.Uri  #: The canonical web URL the embed represents (typically the URL the user pasted into the composer). Used as the returned view's `uri`. May be used for validation in the future.


class ParamsDict(t.TypedDict):
    uris: t.List[
        string_formats.AtUri
    ]  #: AT-URIs of any Atmosphere records that can be resolved and used to construct #externalView views. Example: a site.standard.document and optionally its associated site.standard.publication.
    url: string_formats.Uri  #: The canonical web URL the embed represents (typically the URL the user pasted into the composer). Used as the returned view's `uri`. May be used for validation in the future.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.embed.getEmbedExternalView`."""

    associated_records: t.Optional[t.List['UnknownType']] = (
        None  #: Associated records. The raw record data of the Atmosphere records that backed this view. This is returned for convenience, to avoid the need for the client to separately fetch the record data for the associatedRefs. Example: the site.standard.document and site.standard.publication records that backed this view.
    )
    associated_refs: t.Optional[t.List['models.ComAtprotoRepoStrongRef.Main']] = (
        None  #: StrongRefs (URI+CID) of the Atmosphere records that backed this view, suitable for embedding into a post's external.associatedRefs.
    )
    view: t.Optional['models.AppBskyEmbedExternal.View'] = (
        None  #: Hydrated view of the embed. Present only when the resolved records back the requested URL and supply enough information to populate the required `viewExternal` fields. Omitted alongside the rest of the response when no records resolved or validation failed.
    )
