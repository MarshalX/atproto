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
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereExploreArticleRecommendations`."""

    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    viewer: t.Optional[string_formats.Did] = (
        None  #: DID of the account making the request (not included for public/unauthenticated queries).
    )


class ParamsDict(t.TypedDict):
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    viewer: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: DID of the account making the request (not included for public/unauthenticated queries).


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereExploreArticleRecommendations`."""

    articles: t.List['models.AppBskyUnspeccedGetAtmosphereExploreArticleRecommendations.Article'] = Field(
        max_length=100
    )  #: Articles.
    rec_id_str: str  #: Snowflake for this recommendation, use when submitting recommendation events.


class Article(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereExploreArticleRecommendations`."""

    uri: string_formats.AtUri  #: Uri.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereExploreArticleRecommendations#article'] = Field(
        default='app.bsky.unspecced.getAtmosphereExploreArticleRecommendations#article', alias='$type', frozen=True
    )
