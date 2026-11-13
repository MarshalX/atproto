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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereApps`."""

    category: te.Annotated[t.Optional[str], Field(max_length=100)] = (
        None  #: Only return apps with this category (exact match). Omit to return all apps.
    )


class ParamsDict(t.TypedDict):
    category: te.NotRequired[
        t.Optional[str]
    ]  #: Only return apps with this category (exact match). Omit to return all apps.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereApps`."""

    apps: t.List['models.AppBskyUnspeccedGetAtmosphereApps.AppCard'] = Field(max_length=100)  #: Apps.


class AppCard(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereApps`."""

    app_store_url: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: Optional link to the app on the Apple App Store.
    )
    banner: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: The app's banner, using its account banner when available.
    )
    category: te.Annotated[t.Optional[str], Field(max_length=100)] = None  #: Category.
    description: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Description.
    google_play_url: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: Optional link to the app on Google Play.
    )
    id: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Id.
    logo: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = (
        None  #: The app's logo, using its account avatar when available.
    )
    profile: t.Optional['models.AppBskyActorDefs.ProfileViewDetailed'] = (
        None  #: The app's optional Bluesky account profile. Omitted when no profile is configured or the profile is unavailable.
    )
    title: te.Annotated[t.Optional[str], Field(max_length=4096)] = None  #: Title.
    url: te.Annotated[t.Optional[string_formats.Uri], Field(max_length=4096)] = None  #: Url.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereApps#appCard'] = Field(
        default='app.bsky.unspecced.getAtmosphereApps#appCard', alias='$type', frozen=True
    )
