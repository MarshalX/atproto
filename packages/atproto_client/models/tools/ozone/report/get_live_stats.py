#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.report.getLiveStats`."""

    moderator_did: t.Optional[string_formats.Did] = None  #: Filter stats by moderator DID.
    queue_id: t.Optional[int] = None  #: Filter stats by queue. Use -1 for unqueued reports.
    report_types: t.Optional[t.List[str]] = None  #: Filter stats by report types.


class ParamsDict(t.TypedDict):
    moderator_did: te.NotRequired[t.Optional[string_formats.Did]]  #: Filter stats by moderator DID.
    queue_id: te.NotRequired[t.Optional[int]]  #: Filter stats by queue. Use -1 for unqueued reports.
    report_types: te.NotRequired[t.Optional[t.List[str]]]  #: Filter stats by report types.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.getLiveStats`."""

    stats: 'models.ToolsOzoneReportDefs.LiveStats'  #: Statistics for the requested filter.
