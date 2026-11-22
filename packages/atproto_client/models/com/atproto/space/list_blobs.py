#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.listBlobs`."""

    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.listBlobs`."""

    cids: t.List[string_formats.Cid]  #: Cids.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List[string_formats.Cid]:
        """Get the items of this page."""
        return self.cids
