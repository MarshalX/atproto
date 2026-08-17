#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.createActivity`."""

    activity: te.Annotated[
        t.Union[
            'models.ToolsOzoneReportDefs.QueueActivity',
            'models.ToolsOzoneReportDefs.AssignmentActivity',
            'models.ToolsOzoneReportDefs.EscalationActivity',
            'models.ToolsOzoneReportDefs.CloseActivity',
            'models.ToolsOzoneReportDefs.ReopenActivity',
            'models.ToolsOzoneReportDefs.NoteActivity',
        ],
        Field(discriminator='py_type'),
    ]  #: The type of activity to record.
    event_id: t.Optional[int] = (
        None  #: ID of the report moderation event. Resolves to the report created from that event. Exactly one of reportId or eventId must be provided.
    )
    internal_note: t.Optional[str] = None  #: Optional moderator-only note. Not visible to reporters.
    is_automated: t.Optional[bool] = (
        False  #: Set true when this activity is triggered by an automated process. Defaults to false.
    )
    public_note: t.Optional[str] = None  #: Optional public-facing note, potentially visible to the reporter.
    report_id: t.Optional[int] = (
        None  #: ID of the report to record activity on. Exactly one of reportId or eventId must be provided.
    )


class DataDict(t.TypedDict):
    activity: te.Annotated[
        t.Union[
            'models.ToolsOzoneReportDefs.QueueActivity',
            'models.ToolsOzoneReportDefs.AssignmentActivity',
            'models.ToolsOzoneReportDefs.EscalationActivity',
            'models.ToolsOzoneReportDefs.CloseActivity',
            'models.ToolsOzoneReportDefs.ReopenActivity',
            'models.ToolsOzoneReportDefs.NoteActivity',
        ],
        Field(discriminator='py_type'),
    ]  #: The type of activity to record.
    event_id: te.NotRequired[
        t.Optional[int]
    ]  #: ID of the report moderation event. Resolves to the report created from that event. Exactly one of reportId or eventId must be provided.
    internal_note: te.NotRequired[t.Optional[str]]  #: Optional moderator-only note. Not visible to reporters.
    is_automated: te.NotRequired[
        t.Optional[bool]
    ]  #: Set true when this activity is triggered by an automated process. Defaults to false.
    public_note: te.NotRequired[t.Optional[str]]  #: Optional public-facing note, potentially visible to the reporter.
    report_id: te.NotRequired[
        t.Optional[int]
    ]  #: ID of the report to record activity on. Exactly one of reportId or eventId must be provided.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.createActivity`."""

    activity: 'models.ToolsOzoneReportDefs.ReportActivityView'  #: Activity.
