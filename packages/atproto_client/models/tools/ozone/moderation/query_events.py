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
    """Parameters model for :obj:`tools.ozone.moderation.queryEvents`."""

    added_labels: t.Optional[
        t.List[str]
    ] = None  #: If specified, only events where all of these labels were added are returned.
    added_tags: t.Optional[
        t.List[str]
    ] = None  #: If specified, only events where all of these tags were added are returned.
    comment: t.Optional[str] = None  #: If specified, only events with comments containing the keyword are returned.
    created_after: t.Optional[str] = None  #: Retrieve events created after a given timestamp.
    created_before: t.Optional[str] = None  #: Retrieve events created before a given timestamp.
    created_by: t.Optional[str] = None  #: Created by.
    cursor: t.Optional[str] = None  #: Cursor.
    has_comment: t.Optional[bool] = None  #: If true, only events with comments are returned.
    include_all_user_records: t.Optional[
        bool
    ] = None  #: If true, events on all record types (posts, lists, profile etc.) owned by the did are returned.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    removed_labels: t.Optional[
        t.List[str]
    ] = None  #: If specified, only events where all of these labels were removed are returned.
    removed_tags: t.Optional[
        t.List[str]
    ] = None  #: If specified, only events where all of these tags were removed are returned.
    report_types: t.Optional[t.List[str]] = None  #: Report types.
    sort_direction: t.Optional[
        str
    ] = None  #: Sort direction for the events. Defaults to descending order of created at timestamp.
    subject: t.Optional[str] = None  #: Subject.
    types: t.Optional[
        t.List[str]
    ] = None  #: The types of events (fully qualified string in the format of tools.ozone.moderation.defs#modEvent<name>) to filter by. If not specified, all events are returned.


class ParamsDict(te.TypedDict):
    added_labels: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, only events where all of these labels were added are returned.
    added_tags: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, only events where all of these tags were added are returned.
    comment: te.NotRequired[
        t.Optional[str]
    ]  #: If specified, only events with comments containing the keyword are returned.
    created_after: te.NotRequired[t.Optional[str]]  #: Retrieve events created after a given timestamp.
    created_before: te.NotRequired[t.Optional[str]]  #: Retrieve events created before a given timestamp.
    created_by: te.NotRequired[t.Optional[str]]  #: Created by.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    has_comment: te.NotRequired[t.Optional[bool]]  #: If true, only events with comments are returned.
    include_all_user_records: te.NotRequired[
        t.Optional[bool]
    ]  #: If true, events on all record types (posts, lists, profile etc.) owned by the did are returned.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    removed_labels: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, only events where all of these labels were removed are returned.
    removed_tags: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, only events where all of these tags were removed are returned.
    report_types: te.NotRequired[t.Optional[t.List[str]]]  #: Report types.
    sort_direction: te.NotRequired[
        t.Optional[str]
    ]  #: Sort direction for the events. Defaults to descending order of created at timestamp.
    subject: te.NotRequired[t.Optional[str]]  #: Subject.
    types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: The types of events (fully qualified string in the format of tools.ozone.moderation.defs#modEvent<name>) to filter by. If not specified, all events are returned.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.moderation.queryEvents`."""

    events: t.List['models.ToolsOzoneModerationDefs.ModEventView']  #: Events.
    cursor: t.Optional[str] = None  #: Cursor.
