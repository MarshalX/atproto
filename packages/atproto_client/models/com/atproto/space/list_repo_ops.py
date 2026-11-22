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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.listRepoOps`."""

    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    cursor: t.Optional[str] = None  #: Cursor.
    exclude_values: t.Optional[bool] = False  #: Exclude values.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = None  #: Limit.
    since: t.Optional[string_formats.Tid] = None  #: Since.


class ParamsDict(t.TypedDict):
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    exclude_values: te.NotRequired[t.Optional[bool]]  #: Exclude values.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    since: te.NotRequired[t.Optional[string_formats.Tid]]  #: Since.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.listRepoOps`."""

    commit: 'models.ComAtprotoSpaceDefs.Commit'  #: The repo's current commit. A syncer compares it against its own set hash once it has applied the last page, which has no cursor.
    ops: t.List['models.ComAtprotoSpaceListRepoOps.OpEntry']  #: Ops.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List['models.ComAtprotoSpaceListRepoOps.OpEntry']:
        """Get the items of this page."""
        return self.ops


class OpEntry(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.listRepoOps`. Operations that share a rev were applied in the same commit."""

    collection: string_formats.Nsid  #: Collection.
    rev: string_formats.Tid  #: Rev.
    rkey: string_formats.RecordKey  #: Rkey.
    cid: t.Optional[string_formats.Cid] = None  #: CID of the record after the operation. Null for deletes.
    prev: t.Optional[string_formats.Cid] = None  #: CID of the record before the operation. Null for creates.
    value: t.Optional['UnknownType'] = (
        None  #: Omitted for deletes, if excludeValues is set, or if the record has since changed.
    )

    py_type: t.Literal['com.atproto.space.listRepoOps#opEntry'] = Field(
        default='com.atproto.space.listRepoOps#opEntry', alias='$type', frozen=True
    )
