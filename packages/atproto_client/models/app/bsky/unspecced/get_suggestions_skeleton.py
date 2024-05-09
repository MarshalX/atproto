##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.unspecced.getSuggestionsSkeleton`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    viewer: t.Optional[
        str
    ] = None  #: DID of the account making the request (not included for public/unauthenticated queries). Used to boost followed accounts in ranking.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    viewer: te.NotRequired[
        t.Optional[str]
    ]  #: DID of the account making the request (not included for public/unauthenticated queries). Used to boost followed accounts in ranking.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.unspecced.getSuggestionsSkeleton`."""

    actors: t.List['models.AppBskyUnspeccedDefs.SkeletonSearchActor']  #: Actors.
    cursor: t.Optional[str] = None  #: Cursor.
