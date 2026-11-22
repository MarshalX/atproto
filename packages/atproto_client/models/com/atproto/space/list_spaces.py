#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import bytes_type, string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.listSpaces`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    space_did: t.Optional[string_formats.Did] = None  #: Filter to spaces with this DID as their authority.
    space_type: t.Optional[string_formats.Nsid] = None  #: Space type.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    space_did: te.NotRequired[t.Optional[string_formats.Did]]  #: Filter to spaces with this DID as their authority.
    space_type: te.NotRequired[t.Optional[string_formats.Nsid]]  #: Space type.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.listSpaces`."""

    spaces: t.List['models.ComAtprotoSpaceListSpaces.SpaceView']  #: Spaces.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List['models.ComAtprotoSpaceListSpaces.SpaceView']:
        """Get the items of this page."""
        return self.spaces


class SpaceView(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.listSpaces`."""

    space: string_formats.SpaceRef  #: Space.
    data: t.Optional[bytes_type.BytesType] = (
        None  #: The current commit data of the account's repo in the space, if it has one.
    )
    repo_rev: t.Optional[string_formats.Tid] = (
        None  #: The current revision of the account's repo in the space, if it has one.
    )
    space_rev: t.Optional[string_formats.Tid] = (
        None  #: The current revision of the space. Only included if the account is the space's authority.
    )

    py_type: t.Literal['com.atproto.space.listSpaces#spaceView'] = Field(
        default='com.atproto.space.listSpaces#spaceView', alias='$type', frozen=True
    )
