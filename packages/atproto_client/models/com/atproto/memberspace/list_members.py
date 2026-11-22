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
    """Parameters model for :obj:`com.atproto.memberspace.listMembers`."""

    space: string_formats.SpaceRef  #: Space.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    space: string_formats.SpaceRef  #: Space.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.memberspace.listMembers`."""

    members: t.List['models.ComAtprotoMemberspaceDefs.Member']  #: Members.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List['models.ComAtprotoMemberspaceDefs.Member']:
        """Get the items of this page."""
        return self.members
