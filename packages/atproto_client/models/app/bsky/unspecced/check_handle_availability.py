##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.checkHandleAvailability`."""

    handle: (
        string_formats.Handle
    )  #: Tentative handle. Will be checked for availability or used to build handle suggestions.
    birth_date: t.Optional[string_formats.DateTime] = (
        None  #: User-provided birth date. Might be used to build handle suggestions.
    )
    email: t.Optional[str] = None  #: User-provided email. Might be used to build handle suggestions.


class ParamsDict(t.TypedDict):
    handle: (
        string_formats.Handle
    )  #: Tentative handle. Will be checked for availability or used to build handle suggestions.
    birth_date: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: User-provided birth date. Might be used to build handle suggestions.
    email: te.NotRequired[t.Optional[str]]  #: User-provided email. Might be used to build handle suggestions.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.checkHandleAvailability`."""

    handle: string_formats.Handle  #: Echo of the input handle.
    result: te.Annotated[
        t.Union[
            'models.AppBskyUnspeccedCheckHandleAvailability.ResultAvailable',
            'models.AppBskyUnspeccedCheckHandleAvailability.ResultUnavailable',
        ],
        Field(discriminator='py_type'),
    ]  #: Result.


class ResultAvailable(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.checkHandleAvailability`. Indicates the provided handle is available."""

    py_type: t.Literal['app.bsky.unspecced.checkHandleAvailability#resultAvailable'] = Field(
        default='app.bsky.unspecced.checkHandleAvailability#resultAvailable', alias='$type', frozen=True
    )


class ResultUnavailable(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.checkHandleAvailability`. Indicates the provided handle is unavailable and gives suggestions of available handles."""

    suggestions: t.List[
        'models.AppBskyUnspeccedCheckHandleAvailability.Suggestion'
    ]  #: List of suggested handles based on the provided inputs.

    py_type: t.Literal['app.bsky.unspecced.checkHandleAvailability#resultUnavailable'] = Field(
        default='app.bsky.unspecced.checkHandleAvailability#resultUnavailable', alias='$type', frozen=True
    )


class Suggestion(base.ModelBase):
    """Definition model for :obj:`app.bsky.unspecced.checkHandleAvailability`."""

    handle: string_formats.Handle  #: Handle.
    method: (
        str  #: Method used to build this suggestion. Should be considered opaque to clients. Can be used for metrics.
    )

    py_type: t.Literal['app.bsky.unspecced.checkHandleAvailability#suggestion'] = Field(
        default='app.bsky.unspecced.checkHandleAvailability#suggestion', alias='$type', frozen=True
    )
