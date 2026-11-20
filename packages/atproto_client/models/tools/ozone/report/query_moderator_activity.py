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
    """Parameters model for :obj:`tools.ozone.report.queryModeratorActivity`."""

    created_after: string_formats.DateTime  #: Inclusive UTC lower bound.
    created_before: string_formats.DateTime  #: Exclusive UTC upper bound.
    moderator: string_formats.Did  #: Moderator.
    cursor: te.Annotated[t.Optional[str], Field(max_length=512)] = None  #: Cursor.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    types: te.Annotated[t.Optional[t.List[str]], Field(max_length=40)] = None  #: Types.


class ParamsDict(t.TypedDict):
    created_after: string_formats.DateTime  #: Inclusive UTC lower bound.
    created_before: string_formats.DateTime  #: Exclusive UTC upper bound.
    moderator: string_formats.Did  #: Moderator.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    types: te.NotRequired[t.Optional[t.List[str]]]  #: Types.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.queryModeratorActivity`."""

    rows: t.List['models.ToolsOzoneReportQueryModeratorActivity.ActivityRow']  #: Rows.
    cursor: t.Optional[str] = None  #: Cursor.

    def get_page_items(self) -> t.List['models.ToolsOzoneReportQueryModeratorActivity.ActivityRow']:
        """Get the items of this page."""
        return self.rows


class ActivityRow(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.queryModeratorActivity`."""

    created_at: string_formats.DateTime  #: Created at.
    created_by: string_formats.Did  #: Created by.
    id: int  #: Id.
    source: t.Literal['event', 'activity']  #: Source.
    type: str  #: Type.
    action_event_id: t.Optional[int] = None  #: Action event id.
    activity: t.Optional['models.ToolsOzoneReportDefs.ReportActivityView'] = None  #: Activity.
    event: t.Optional['models.ToolsOzoneModerationDefs.ModEventView'] = None  #: Event.
    report_id: t.Optional[int] = None  #: Report id.
    subject: t.Optional[str] = None  #: Subject.

    py_type: t.Literal['tools.ozone.report.queryModeratorActivity#activityRow'] = Field(
        default='tools.ozone.report.queryModeratorActivity#activityRow', alias='$type', frozen=True
    )
