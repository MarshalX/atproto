#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.report.closeReports`."""

    subject: (
        string_formats.Uri
    )  #: Subject DID (account-level reports) or AT-URI (record-level reports) whose reports should be closed.
    internal_note: t.Optional[str] = (
        None  #: Optional moderator-only note recorded on each close activity. Not visible to reporters.
    )
    is_automated: t.Optional[bool] = (
        False  #: Set true when this action is triggered by an automated process. Defaults to false.
    )
    report_types: t.Optional[t.List[str]] = (
        None  #: If specified, only reports of the given report types (fully qualified reason NSIDs) are closed. When omitted, all non-closed reports on the subject are targeted.
    )


class DataDict(t.TypedDict):
    subject: (
        string_formats.Uri
    )  #: Subject DID (account-level reports) or AT-URI (record-level reports) whose reports should be closed.
    internal_note: te.NotRequired[
        t.Optional[str]
    ]  #: Optional moderator-only note recorded on each close activity. Not visible to reporters.
    is_automated: te.NotRequired[
        t.Optional[bool]
    ]  #: Set true when this action is triggered by an automated process. Defaults to false.
    report_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, only reports of the given report types (fully qualified reason NSIDs) are closed. When omitted, all non-closed reports on the subject are targeted.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.report.closeReports`."""

    closed_count: int  #: Number of reports that were transitioned to closed.
    report_ids: t.List[int]  #: IDs of the reports that were closed.
