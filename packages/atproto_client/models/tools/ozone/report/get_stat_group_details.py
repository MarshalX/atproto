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
    """Parameters model for :obj:`tools.ozone.report.getStatGroupDetails`."""

    end_date: t.Optional[string_formats.DateTime] = (
        None  #: Last UTC calendar day to include, inclusive. Defaults to today.
    )
    moderator_did: t.Optional[string_formats.Did] = (
        None  #: Moderator stat group, based on current report assignment. Requires administrator access.
    )
    queue_id: te.Annotated[t.Optional[int], Field(ge=-1)] = (
        None  #: Queue stat group. Use -1 for unqueued reports; otherwise use a positive queue ID. Requires queue access.
    )
    report_types: te.Annotated[t.Optional[t.List[str]], Field(min_length=1, max_length=100)] = (
        None  #: Report-type stat group. Counts only the specified reasons.
    )
    start_date: t.Optional[string_formats.DateTime] = (
        None  #: First UTC calendar day to include, inclusive. Defaults to today. The range must not exceed 120 calendar days.
    )


class ParamsDict(t.TypedDict):
    end_date: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Last UTC calendar day to include, inclusive. Defaults to today.
    moderator_did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Moderator stat group, based on current report assignment. Requires administrator access.
    queue_id: te.NotRequired[
        t.Optional[int]
    ]  #: Queue stat group. Use -1 for unqueued reports; otherwise use a positive queue ID. Requires queue access.
    report_types: te.NotRequired[t.Optional[t.List[str]]]  #: Report-type stat group. Counts only the specified reasons.
    start_date: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: First UTC calendar day to include, inclusive. Defaults to today. The range must not exceed 120 calendar days.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.getStatGroupDetails`."""

    computed_at: string_formats.DateTime  #: When the live query started.
    end_date: string_formats.DateTime  #: Last included UTC calendar day, at midnight.
    report_type_breakdown: 'models.ToolsOzoneReportGetStatGroupDetails.ReportTypeBreakdown'  #: Report type breakdown.
    start_date: string_formats.DateTime  #: First included UTC calendar day, at midnight.


class ReportTypeStats(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.getStatGroupDetails`."""

    inbound_count: int = Field(ge=0)  #: Unmuted reports received during the requested UTC calendar days.
    report_type: str  #: Fully qualified report reason.

    py_type: t.Literal['tools.ozone.report.getStatGroupDetails#reportTypeStats'] = Field(
        default='tools.ozone.report.getStatGroupDetails#reportTypeStats', alias='$type', frozen=True
    )


class ReportTypeBreakdown(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.getStatGroupDetails`. Unmuted inbound reports by actual reason, across all statuses, within the selected stat group and UTC date range."""

    stats: t.List['models.ToolsOzoneReportGetStatGroupDetails.ReportTypeStats']  #: Stats.
    total_count: int = Field(ge=0)  #: Total unmuted inbound reports in this breakdown.

    py_type: t.Literal['tools.ozone.report.getStatGroupDetails#reportTypeBreakdown'] = Field(
        default='tools.ozone.report.getStatGroupDetails#reportTypeBreakdown', alias='$type', frozen=True
    )
