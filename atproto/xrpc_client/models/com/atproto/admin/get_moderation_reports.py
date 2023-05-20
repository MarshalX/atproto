##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.getModerationReports`.

    Attributes:
        subject: Subject.
        resolved: Resolved.
        actionType: Action type.
        limit: Limit.
        cursor: Cursor.
    """

    actionType: t.Optional[str] = None
    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None
    resolved: t.Optional[bool] = None
    subject: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.getModerationReports`.

    Attributes:
        cursor: Cursor.
        reports: Reports.
    """

    reports: t.List['models.ComAtprotoAdminDefs.ReportView']
    cursor: t.Optional[str] = None
