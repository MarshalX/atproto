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

    """Parameters model for :obj:`app.bsky.actor.searchActors`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=25, ge=1, le=100)  #: Limit.
    q: t.Optional[
        str
    ] = None  #: Search query string. Syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.
    term: t.Optional[str] = None  #: DEPRECATED: use 'q' instead.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    q: te.NotRequired[
        t.Optional[str]
    ]  #: Search query string. Syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.
    term: te.NotRequired[t.Optional[str]]  #: DEPRECATED: use 'q' instead.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.actor.searchActors`."""

    actors: t.List['models.AppBskyActorDefs.ProfileView']  #: Actors.
    cursor: t.Optional[str] = None  #: Cursor.
