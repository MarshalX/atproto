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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getTaggedSuggestions`."""


class ParamsDict(te.TypedDict):
    pass


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getTaggedSuggestions`."""

    suggestions: t.List['models.AppBskyUnspeccedGetTaggedSuggestions.Suggestion']  #: Suggestions.


class Suggestion(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.getTaggedSuggestions`."""

    subject: str  #: Subject.
    subject_type: str  #: Subject type.
    tag: str  #: Tag.

    py_type: te.Literal['app.bsky.unspecced.getTaggedSuggestions#suggestion'] = Field(
        default='app.bsky.unspecced.getTaggedSuggestions#suggestion', alias='$type', frozen=True
    )
