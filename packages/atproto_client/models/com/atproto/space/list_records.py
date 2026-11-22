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
    """Parameters model for :obj:`com.atproto.space.listRecords`."""

    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    collection: t.Optional[string_formats.Nsid] = None  #: If omitted, lists records across all collections.
    cursor: t.Optional[str] = None  #: Cursor.
    exclude_values: t.Optional[bool] = False  #: Exclude values.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    collection: te.NotRequired[t.Optional[string_formats.Nsid]]  #: If omitted, lists records across all collections.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    exclude_values: te.NotRequired[t.Optional[bool]]  #: Exclude values.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.listRecords`."""

    records: t.List['models.ComAtprotoSpaceListRecords.Record']  #: Records.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List['models.ComAtprotoSpaceListRecords.Record']:
        """Get the items of this page."""
        return self.records


class Record(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.listRecords`."""

    cid: string_formats.Cid  #: Cid.
    collection: string_formats.Nsid  #: Collection.
    rkey: string_formats.RecordKey  #: Rkey.
    value: t.Optional['UnknownType'] = None  #: Value.

    py_type: t.Literal['com.atproto.space.listRecords#record'] = Field(
        default='com.atproto.space.listRecords#record', alias='$type', frozen=True
    )
