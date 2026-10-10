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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.getReport`."""

    id: int  #: Report ID (report table ID), as returned by listReports.
    did: t.Optional[string_formats.Did] = (
        None  #: Reporter to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    )


class ParamsDict(t.TypedDict):
    id: int  #: Report ID (report table ID), as returned by listReports.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Reporter to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.getReport`."""

    report: 'models.ToolsOzoneInboxGetReport.ReportView'  #: Report.
    resolution: t.Optional['models.ToolsOzoneInboxGetReport.ResolutionView'] = (
        None  #: Present only when the report is resolved.
    )


class ReportView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.getReport`."""

    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Report ID (report table ID), used by Ozone's report detail page.
    reason_type: str  #: The exact fully-qualified reason NSID submitted with and stored on the report.
    src: string_formats.Did  #: DID of the moderation service that received the report.
    status: t.Union[t.Literal['pending', 'resolved'], str]  #: Status.
    subject: unknown_union.OpenUnion[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoRef',
            'models.ComAtprotoRepoStrongRef.Main',
            'models.ChatBskyConvoDefs.MessageRef',
            'models.ChatBskyConvoDefs.ConvoRef',
        ]
    ]  #: Subject.
    updated_at: string_formats.DateTime  #: Updated at.
    reason: te.Annotated[t.Optional[str], Field(max_length=20000)] = None  #: Reason.
    record: t.Optional['UnknownType'] = (
        None  #: Raw record JSON for the subject, when the subject is a record and the record is available.
    )

    py_type: t.Literal['tools.ozone.inbox.getReport#reportView'] = Field(
        default='tools.ozone.inbox.getReport#reportView', alias='$type', frozen=True
    )


class ResolutionView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.getReport`."""

    outcome: t.Union[t.Literal['actionTaken', 'noAction', 'other'], str]  #: Outcome.
    resolved_at: string_formats.DateTime  #: Resolved at.
    action_taken: t.Optional[str] = (
        None  #: Public action associated with this report's resolution. See the public action vocabulary table.
    )
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.getReport#resolutionView'] = Field(
        default='tools.ozone.inbox.getReport#resolutionView', alias='$type', frozen=True
    )
