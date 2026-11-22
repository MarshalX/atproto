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
    """Parameters model for :obj:`com.atproto.space.listWriters`."""

    space: string_formats.SpaceRef  #: Space.
    cursor: t.Optional[str] = (
        None  #: Return repos updated after this space revision. Removed repos may be garbage collected after 72 hrs, so a syncer whose last seen space revision is older should list the whole writer set instead.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    space: string_formats.SpaceRef  #: Space.
    cursor: te.NotRequired[
        t.Optional[str]
    ]  #: Return repos updated after this space revision. Removed repos may be garbage collected after 72 hrs, so a syncer whose last seen space revision is older should list the whole writer set instead.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.listWriters`."""

    repos: t.List[
        unknown_union.OpenUnion[
            t.Union['models.ComAtprotoSpaceDefs.RepoWrite', 'models.ComAtprotoSpaceDefs.RepoRemoved']
        ]
    ]  #: The latest update to each repo, ordered by spaceRev, ascending. prevSpaceRev is not set.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(
        self,
    ) -> t.List[
        unknown_union.OpenUnion[
            t.Union['models.ComAtprotoSpaceDefs.RepoWrite', 'models.ComAtprotoSpaceDefs.RepoRemoved']
        ]
    ]:
        """Get the items of this page."""
        return self.repos
