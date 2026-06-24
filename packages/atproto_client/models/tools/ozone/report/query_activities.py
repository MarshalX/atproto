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
    """Parameters model for :obj:`tools.ozone.report.queryActivities`."""

    activity_types: t.Optional[t.List[str]] = (
        None  #: Filter to specific activity types (e.g. closeActivity, escalationActivity). If omitted, all types are returned.
    )
    created_after: t.Optional[string_formats.DateTime] = (
        None  #: Retrieve activities created at or after a given timestamp.
    )
    created_before: t.Optional[string_formats.DateTime] = (
        None  #: Retrieve activities created at or before a given timestamp.
    )
    cursor: t.Optional[str] = None  #: Cursor of the form `<createdAtMs>::<activityId>`.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    sort_direction: t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]] = 'desc'  #: Sort direction.


class ParamsDict(t.TypedDict):
    activity_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Filter to specific activity types (e.g. closeActivity, escalationActivity). If omitted, all types are returned.
    created_after: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Retrieve activities created at or after a given timestamp.
    created_before: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Retrieve activities created at or before a given timestamp.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor of the form `<createdAtMs>::<activityId>`.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    sort_direction: te.NotRequired[t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]]]  #: Sort direction.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.queryActivities`."""

    activities: t.List['models.ToolsOzoneReportDefs.ReportActivityView']  #: Activities.
    cursor: t.Optional[str] = None  #: Cursor.
