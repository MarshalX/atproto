##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.report.getHistoricalStats`."""

    cursor: t.Optional[str] = None  #: Pagination cursor.
    end_date: t.Optional[string_formats.DateTime] = None  #: Latest date to include (inclusive).
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Maximum number of entries to return.
    moderator_did: t.Optional[string_formats.Did] = None  #: Filter stats by moderator DID.
    queue_id: t.Optional[int] = None  #: Filter stats by queue. Use -1 for unqueued reports.
    report_types: t.Optional[t.List[str]] = None  #: Filter stats by report types.
    start_date: t.Optional[string_formats.DateTime] = None  #: Earliest date to include (inclusive).


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Pagination cursor.
    end_date: te.NotRequired[t.Optional[string_formats.DateTime]]  #: Latest date to include (inclusive).
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of entries to return.
    moderator_did: te.NotRequired[t.Optional[string_formats.Did]]  #: Filter stats by moderator DID.
    queue_id: te.NotRequired[t.Optional[int]]  #: Filter stats by queue. Use -1 for unqueued reports.
    report_types: te.NotRequired[t.Optional[t.List[str]]]  #: Filter stats by report types.
    start_date: te.NotRequired[t.Optional[string_formats.DateTime]]  #: Earliest date to include (inclusive).


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.getHistoricalStats`."""

    stats: t.List['models.ToolsOzoneReportDefs.HistoricalStats']  #: Stats.
    cursor: t.Optional[str] = None  #: Cursor.
