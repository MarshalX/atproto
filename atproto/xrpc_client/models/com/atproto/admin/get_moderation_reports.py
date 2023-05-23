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

    """Parameters model for :obj:`com.atproto.admin.getModerationReports`."""

    actionType: t.Optional[str] = None  #: Action type.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = None  #: Limit.
    resolved: t.Optional[bool] = None  #: Resolved.
    subject: t.Optional[str] = None  #: Subject.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.getModerationReports`."""

    reports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Reports.
    cursor: t.Optional[str] = None  #: Cursor.
