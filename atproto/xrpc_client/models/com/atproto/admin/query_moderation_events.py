##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.queryModerationEvents`."""

    created_by: t.Optional[str] = Field(default=None, alias='createdBy')  #: Created by.
    cursor: t.Optional[str] = None  #: Cursor.
    include_all_user_records: t.Optional[bool] = Field(
        default=False, alias='includeAllUserRecords'
    )  #: If true, events on all record types (posts, lists, profile etc.) owned by the did are returned.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    sort_direction: t.Optional[str] = Field(
        default='desc', alias='sortDirection'
    )  #: Sort direction for the events. Defaults to descending order of created at timestamp.
    subject: t.Optional[str] = None  #: Subject.
    types: t.Optional[
        t.List[str]
    ] = None  #: The types of events (fully qualified string in the format of com.atproto.admin#modEvent<name>) to filter by. If not specified, all events are returned.


class ParamsDict(te.TypedDict):
    created_by: te.NotRequired[t.Optional[str]]  #: Created by.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    include_all_user_records: te.NotRequired[
        t.Optional[bool]
    ]  #: If true, events on all record types (posts, lists, profile etc.) owned by the did are returned.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    sort_direction: te.NotRequired[
        t.Optional[str]
    ]  #: Sort direction for the events. Defaults to descending order of created at timestamp.
    subject: te.NotRequired[t.Optional[str]]  #: Subject.
    types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: The types of events (fully qualified string in the format of com.atproto.admin#modEvent<name>) to filter by. If not specified, all events are returned.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.queryModerationEvents`."""

    events: t.List['models.ComAtprotoAdminDefs.ModEventView']  #: Events.
    cursor: t.Optional[str] = None  #: Cursor.
