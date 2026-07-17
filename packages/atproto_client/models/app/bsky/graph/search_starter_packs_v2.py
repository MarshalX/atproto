#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.graph.searchStarterPacksV2`."""

    q: str  #: Search query string. Syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    q: str  #: Search query string. Syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.graph.searchStarterPacksV2`."""

    starter_packs: t.List['models.AppBskyGraphDefs.StarterPackView']  #: Starter packs.
    cursor: t.Optional[str] = None  #: Cursor.
    hits_total: t.Optional[int] = None  #: Estimated total number of matching hits. May be rounded or truncated.
