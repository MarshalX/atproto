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
    """Parameters model for :obj:`tools.ozone.report.queryReports`."""

    status: t.Union[
        t.Literal['open'], t.Literal['closed'], t.Literal['escalated'], t.Literal['queued'], t.Literal['assigned'], str
    ]  #: Filter by report status.
    assigned_to: t.Optional[string_formats.Did] = (
        None  #: Filter by the DID of the moderator permanently assigned to the report.
    )
    collections: te.Annotated[t.Optional[t.List[string_formats.Nsid]], Field(max_length=20)] = (
        None  #: If specified, reports where the subject belongs to the given collections will be returned. When subjectType is set to 'account', this will be ignored.
    )
    cursor: t.Optional[str] = None  #: Cursor.
    did: t.Optional[string_formats.Did] = (
        None  #: Filter to reports where the subject is this DID or any record owned by this DID. Unlike `subject` (which scopes to a specific account or record), this returns all reports tied to the DID across both account-level and record-level subjects.
    )
    is_muted: t.Optional[bool] = (
        False  #: Filter by muted status. true returns only muted reports, false returns only unmuted reports. Defaults to false.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    queue_id: t.Optional[int] = None  #: Filter by queue ID. Use -1 for unassigned reports.
    report_types: t.Optional[t.List[str]] = (
        None  #: Filter by report types (fully qualified string in the format of com.atproto.moderation.defs#reason<name>).
    )
    reported_after: t.Optional[string_formats.DateTime] = None  #: Retrieve reports created after a given timestamp.
    reported_before: t.Optional[string_formats.DateTime] = None  #: Retrieve reports created before a given timestamp.
    sort_direction: t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]] = 'desc'  #: Sort direction.
    sort_field: t.Optional[t.Union[t.Literal['createdAt'], t.Literal['updatedAt']]] = 'createdAt'  #: Sort field.
    subject: t.Optional[string_formats.Uri] = None  #: Filter by subject DID or AT-URI.
    subject_type: t.Optional[t.Union[t.Literal['account'], t.Literal['record'], str]] = (
        None  #: If specified, reports of the given type (account or record) will be returned.
    )


class ParamsDict(t.TypedDict):
    status: t.Union[
        t.Literal['open'], t.Literal['closed'], t.Literal['escalated'], t.Literal['queued'], t.Literal['assigned'], str
    ]  #: Filter by report status.
    assigned_to: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Filter by the DID of the moderator permanently assigned to the report.
    collections: te.NotRequired[
        t.Optional[t.List[string_formats.Nsid]]
    ]  #: If specified, reports where the subject belongs to the given collections will be returned. When subjectType is set to 'account', this will be ignored.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Filter to reports where the subject is this DID or any record owned by this DID. Unlike `subject` (which scopes to a specific account or record), this returns all reports tied to the DID across both account-level and record-level subjects.
    is_muted: te.NotRequired[
        t.Optional[bool]
    ]  #: Filter by muted status. true returns only muted reports, false returns only unmuted reports. Defaults to false.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    queue_id: te.NotRequired[t.Optional[int]]  #: Filter by queue ID. Use -1 for unassigned reports.
    report_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Filter by report types (fully qualified string in the format of com.atproto.moderation.defs#reason<name>).
    reported_after: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Retrieve reports created after a given timestamp.
    reported_before: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Retrieve reports created before a given timestamp.
    sort_direction: te.NotRequired[t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]]]  #: Sort direction.
    sort_field: te.NotRequired[t.Optional[t.Union[t.Literal['createdAt'], t.Literal['updatedAt']]]]  #: Sort field.
    subject: te.NotRequired[t.Optional[string_formats.Uri]]  #: Filter by subject DID or AT-URI.
    subject_type: te.NotRequired[
        t.Optional[t.Union[t.Literal['account'], t.Literal['record'], str]]
    ]  #: If specified, reports of the given type (account or record) will be returned.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.queryReports`."""

    reports: t.List['models.ToolsOzoneReportDefs.ReportView']  #: Reports.
    cursor: t.Optional[str] = None  #: Cursor.
