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
    """Parameters model for :obj:`tools.ozone.report.getAssignments`."""

    cursor: t.Optional[str] = None  #: Cursor.
    dids: te.Annotated[t.Optional[t.List[string_formats.Did]], Field(max_length=50)] = (
        None  #: If specified, returns assignments for these moderators only.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    only_active: t.Optional[bool] = True  #: When true, only returns active assignments.
    report_ids: te.Annotated[t.Optional[t.List[int]], Field(max_length=50)] = (
        None  #: If specified, returns assignments for these reports only.
    )


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    dids: te.NotRequired[
        t.Optional[t.List[string_formats.Did]]
    ]  #: If specified, returns assignments for these moderators only.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    only_active: te.NotRequired[t.Optional[bool]]  #: When true, only returns active assignments.
    report_ids: te.NotRequired[t.Optional[t.List[int]]]  #: If specified, returns assignments for these reports only.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.getAssignments`."""

    assignments: t.List['models.ToolsOzoneReportDefs.AssignmentView']  #: Assignments.
    cursor: t.Optional[str] = None  #: Cursor.
