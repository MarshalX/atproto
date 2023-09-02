##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.getModerationReports`."""

    action_type: t.Optional[str] = Field(default=None, alias='actionType')  #: Action type.
    actioned_by: t.Optional[str] = Field(
        default=None, alias='actionedBy'
    )  #: Get all reports that were actioned by a specific moderator.
    cursor: t.Optional[str] = None  #: Cursor.
    ignore_subjects: t.Optional[t.List[str]] = Field(default=None, alias='ignoreSubjects')  #: Ignore subjects.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    reporters: t.Optional[t.List[str]] = None  #: Filter reports made by one or more DIDs.
    resolved: t.Optional[bool] = None  #: Resolved.
    reverse: t.Optional[
        bool
    ] = None  #: Reverse the order of the returned records? when true, returns reports in chronological order.
    subject: t.Optional[str] = None  #: Subject.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.getModerationReports`."""

    reports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Reports.
    cursor: t.Optional[str] = None  #: Cursor.
