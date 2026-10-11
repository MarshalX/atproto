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
from atproto_client.models import base, unknown_union


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.listReports`."""

    cursor: t.Optional[str] = None  #: An opaque cursor for pagination.
    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    )
    filter: t.Optional[t.Literal['all', 'pending', 'resolved', 'unread']] = (
        'all'  #: Filter report activity. unread includes reports whose updatedAt is after the reports section's seenAt watermark.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    sort_direction: t.Optional[t.Literal['asc', 'desc']] = 'desc'  #: Sort direction.
    sort_field: t.Optional[t.Literal['createdAt', 'updatedAt']] = 'updatedAt'  #: Sort field.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: An opaque cursor for pagination.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    filter: te.NotRequired[
        t.Optional[t.Literal['all', 'pending', 'resolved', 'unread']]
    ]  #: Filter report activity. unread includes reports whose updatedAt is after the reports section's seenAt watermark.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    sort_direction: te.NotRequired[t.Optional[t.Literal['asc', 'desc']]]  #: Sort direction.
    sort_field: te.NotRequired[t.Optional[t.Literal['createdAt', 'updatedAt']]]  #: Sort field.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.listReports`."""

    reports: t.List['models.ToolsOzoneInboxListReports.ReportView']  #: Reports.
    cursor: t.Optional[str] = None  #: Cursor.


class ReportView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.listReports`."""

    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Report ID (report table ID), used by getReport and Ozone's report detail page.
    is_read: bool  #: Is read.
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
    last_action_taken: t.Optional[str] = (
        None  #: Public action associated with this report's transition to resolved. See the public action vocabulary table.
    )
    reason: te.Annotated[t.Optional[str], Field(max_length=20000)] = None  #: Reason.
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.listReports#reportView'] = Field(
        default='tools.ozone.inbox.listReports#reportView', alias='$type', frozen=True
    )
