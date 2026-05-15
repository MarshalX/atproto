##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.reassignQueue`."""

    queue_id: int  #: Target queue ID. Use -1 to unassign from any queue.
    report_id: int  #: ID of the report to reassign.
    comment: t.Optional[str] = (
        None  #: Optional moderator-only note recorded on the resulting queueActivity as internalNote.
    )


class DataDict(t.TypedDict):
    queue_id: int  #: Target queue ID. Use -1 to unassign from any queue.
    report_id: int  #: ID of the report to reassign.
    comment: te.NotRequired[
        t.Optional[str]
    ]  #: Optional moderator-only note recorded on the resulting queueActivity as internalNote.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.reassignQueue`."""

    report: 'models.ToolsOzoneReportDefs.ReportView'  #: Report.
