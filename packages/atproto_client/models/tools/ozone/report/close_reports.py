#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownInputType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.closeReports`."""

    subject: (
        string_formats.Uri
    )  #: Subject DID (account-level reports) or AT-URI (record-level reports) whose reports should be closed.
    excluded_report_types: t.Optional[t.List[str]] = (
        None  #: Reports of these types (fully qualified reason NSIDs) are excluded from closure and left unchanged. When omitted or empty, no report types are excluded.
    )
    include_all_owned: t.Optional[bool] = (
        False  #: If true, also close reports on all subjects owned by the account, including records, messages, and conversations. Only valid when subject is an account DID.
    )
    internal_note: t.Optional[str] = (
        None  #: Optional moderator-only note recorded on each close activity. Not visible to reporters.
    )
    is_automated: t.Optional[bool] = (
        False  #: Set true when this action is triggered by an automated process. Defaults to false.
    )
    meta: t.Optional['UnknownInputType'] = (
        None  #: Optional metadata for the report activities. Lifecycle and resolution fields are controlled by the service.
    )
    report_types: t.Optional[t.List[str]] = (
        None  #: If nonempty, only reports of the given report types (fully qualified reason NSIDs) are closed. When omitted or empty, all eligible reports in the requested subject scope are targeted, except excludedReportTypes. Assigned and escalated reports are always excluded.
    )


class DataDict(t.TypedDict):
    subject: (
        string_formats.Uri
    )  #: Subject DID (account-level reports) or AT-URI (record-level reports) whose reports should be closed.
    excluded_report_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Reports of these types (fully qualified reason NSIDs) are excluded from closure and left unchanged. When omitted or empty, no report types are excluded.
    include_all_owned: te.NotRequired[
        t.Optional[bool]
    ]  #: If true, also close reports on all subjects owned by the account, including records, messages, and conversations. Only valid when subject is an account DID.
    internal_note: te.NotRequired[
        t.Optional[str]
    ]  #: Optional moderator-only note recorded on each close activity. Not visible to reporters.
    is_automated: te.NotRequired[
        t.Optional[bool]
    ]  #: Set true when this action is triggered by an automated process. Defaults to false.
    meta: te.NotRequired[
        t.Optional['UnknownInputType']
    ]  #: Optional metadata for the report activities. Lifecycle and resolution fields are controlled by the service.
    report_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If nonempty, only reports of the given report types (fully qualified reason NSIDs) are closed. When omitted or empty, all eligible reports in the requested subject scope are targeted, except excludedReportTypes. Assigned and escalated reports are always excluded.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.closeReports`."""

    closed_count: int  #: Number of reports that were transitioned to closed.
    report_ids: t.List[int]  #: IDs of the reports that were closed.
