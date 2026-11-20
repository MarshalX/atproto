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
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getAtmosphereRecommendedActivity`."""

    langs: t.Optional[t.List[string_formats.Language]] = (
        None  #: Preferred languages for article recommendations. Overrides the Accept-Language header when nonempty.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    langs: te.NotRequired[
        t.Optional[t.List[string_formats.Language]]
    ]  #: Preferred languages for article recommendations. Overrides the Accept-Language header when nonempty.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getAtmosphereRecommendedActivity`."""

    items: t.List['models.AppBskyUnspeccedGetAtmosphereRecommendedActivity.Item'] = Field(max_length=100)  #: Items.
    rec_id_str: str  #: Snowflake for this recommendation, use when submitting recommendation events.


class Item(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getAtmosphereRecommendedActivity`."""

    view: unknown_union.OpenUnion[
        t.Union['models.AppBskyEmbedExternal.ViewArticle', 'models.AppBskyEmbedExternal.ViewGallery']
    ]  #: View.

    py_type: t.Literal['app.bsky.unspecced.getAtmosphereRecommendedActivity#item'] = Field(
        default='app.bsky.unspecced.getAtmosphereRecommendedActivity#item', alias='$type', frozen=True
    )
