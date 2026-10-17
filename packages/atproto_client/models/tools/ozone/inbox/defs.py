#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base, unknown_union


class SubjectView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. A subject belonging to the viewer that has moderation actions against it."""

    created_at: string_formats.DateTime  #: Created at.
    enforcement: 'models.ToolsOzoneInboxDefs.EnforcementView'  #: Enforcement.
    is_read: bool  #: Is read.
    src: string_formats.Did  #: DID of the moderation service that took the actions.
    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject.
    updated_at: string_formats.DateTime  #: Updated at.
    action_count: t.Optional[int] = None  #: Action count.
    appeal: t.Optional['models.ToolsOzoneInboxDefs.AppealView'] = None  #: Appeal.
    available_actions: t.Optional[t.List[t.Union[t.Literal['appeal'], str]]] = None  #: Available actions.
    latest_action: t.Optional['models.ToolsOzoneInboxDefs.ActionView'] = None  #: Latest action.

    py_type: t.Literal['tools.ozone.inbox.defs#subjectView'] = Field(
        default='tools.ozone.inbox.defs#subjectView', alias='$type', frozen=True
    )


class EnforcementView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. The current enforcement state of a subject."""

    state: t.Union[t.Literal['none', 'labeled', 'removed', 'suspended', 'takendown'], str]  #: State.
    expires_at: t.Optional[string_formats.DateTime] = None  #: Expires at.
    labels: t.Optional[t.List[str]] = None  #: Active label values on the subject, excluding negated and expired labels.
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.defs#enforcementView'] = Field(
        default='tools.ozone.inbox.defs#enforcementView', alias='$type', frozen=True
    )


class AppealView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. The state of the viewer's appeal against the actions on a subject."""

    state: t.Union[t.Literal['none', 'pending', 'resolved', 'superseded', 'expired'], str]  #: State.
    appealable_until: t.Optional[string_formats.DateTime] = None  #: Appealable until.
    appealed_at: t.Optional[string_formats.DateTime] = None  #: Appealed at.
    outcome: t.Optional[t.Union[t.Literal['approved', 'denied'], str]] = None  #: Decision on a resolved appeal.
    resolved_at: t.Optional[string_formats.DateTime] = None  #: When the appeal's report was closed.

    py_type: t.Literal['tools.ozone.inbox.defs#appealView'] = Field(
        default='tools.ozone.inbox.defs#appealView', alias='$type', frozen=True
    )


class ActionView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. A single moderation action taken against a subject."""

    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Action ID (moderation event ID).
    type: str  #: Public action type.
    expires_at: t.Optional[string_formats.DateTime] = None  #: Expires at.
    labels: t.Optional[t.List[str]] = None  #: Label values, for labelApplied/labelRemoved.
    policies: t.Optional[t.List['models.ToolsOzoneInboxDefs.PolicyView']] = (
        None  #: Policies applied by a takedown action.
    )
    reversed_at: t.Optional[string_formats.DateTime] = None  #: Reversed at.
    scope: t.Optional[t.Union[t.Literal['network', 'app', 'labelOnly'], str]] = None  #: Scope.

    py_type: t.Literal['tools.ozone.inbox.defs#actionView'] = Field(
        default='tools.ozone.inbox.defs#actionView', alias='$type', frozen=True
    )


class PolicyView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`."""

    display_name: str  #: Display name.
    key: str  #: Key.
    link: string_formats.Uri  #: Link.

    py_type: t.Literal['tools.ozone.inbox.defs#policyView'] = Field(
        default='tools.ozone.inbox.defs#policyView', alias='$type', frozen=True
    )


class SubjectViewDetail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. A subject with a page of its action history and an aggregate report summary. Follow cursor to retrieve older actions; enforcement and appeal describe the current subject state on every page."""

    actions: t.List['models.ToolsOzoneInboxDefs.ActionView'] = Field(
        max_length=100
    )  #: A page of action history, most recent first. Reversal timestamps include changes outside this page.
    created_at: string_formats.DateTime  #: Created at.
    enforcement: 'models.ToolsOzoneInboxDefs.EnforcementView'  #: Enforcement.
    is_read: bool  #: Is read.
    src: string_formats.Did  #: Src.
    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject.
    updated_at: string_formats.DateTime  #: Updated at.
    appeal: t.Optional['models.ToolsOzoneInboxDefs.AppealView'] = None  #: Appeal.
    available_actions: t.Optional[t.List[t.Union[t.Literal['appeal'], str]]] = None  #: Available actions.
    cursor: t.Optional[str] = None  #: Cursor for the next page of action history. Omitted when no older actions remain.
    record: t.Optional['UnknownType'] = (
        None  #: Raw record JSON for the subject, when the subject is a record and the record is available.
    )
    reports: t.Optional['models.ToolsOzoneInboxDefs.ReportsSummary'] = (
        None  #: Omitted when the subject has never been reported, e.g. proactive enforcement.
    )

    py_type: t.Literal['tools.ozone.inbox.defs#subjectViewDetail'] = Field(
        default='tools.ozone.inbox.defs#subjectViewDetail', alias='$type', frozen=True
    )


class ReportsSummary(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. Aggregate view of reports filed against this subject. Deliberately carries no report IDs, no count, and no reporter identities."""

    first_reported_on: (
        string_formats.DateTime
    )  #: Day of the earliest report, truncated to midnight UTC. Render as a date; the time component is not meaningful.
    last_reported_on: string_formats.DateTime  #: Day of the most recent report, truncated to midnight UTC. Render as a date; the time component is not meaningful.
    reason_types: t.List[str]  #: Distinct reason types reported, deduplicated and unordered. Excludes reasonAppeal.

    py_type: t.Literal['tools.ozone.inbox.defs#reportsSummary'] = Field(
        default='tools.ozone.inbox.defs#reportsSummary', alias='$type', frozen=True
    )


class Notification(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`."""

    created_at: string_formats.DateTime  #: Created at.
    id: int  #: Id.
    is_read: bool  #: Is read.
    reason: t.Union[
        t.Literal[
            'reportResolved', 'reportReopened', 'actionTaken', 'actionReversed', 'appealResolved', 'standingChanged'
        ],
        str,
    ]  #: Reason.
    target: unknown_union.OpenUnion[
        t.Union[
            'models.ToolsOzoneInboxDefs.ReportRef',
            'models.ToolsOzoneInboxDefs.SubjectRef',
            'models.ToolsOzoneInboxDefs.StandingRef',
        ]
    ]  #: Target.

    py_type: t.Literal['tools.ozone.inbox.defs#notification'] = Field(
        default='tools.ozone.inbox.defs#notification', alias='$type', frozen=True
    )


class NotificationPreferences(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. Push notification preferences by moderation notification category. These preferences do not hide in-app inbox activity. Each category defaults to enabled."""

    account: bool  #: Notify about moderation actions against the account or its content, action reversals, appeal outcomes, and standing changes. Label application and removal are controlled by labels.
    labels: bool  #: Notify when labels are applied to or removed from the account or its content (labelApplied and labelRemoved actions).
    reports: bool  #: Notify about outcomes of reports filed by the account (reportResolved and reportReopened).

    py_type: t.Literal['tools.ozone.inbox.defs#notificationPreferences'] = Field(
        default='tools.ozone.inbox.defs#notificationPreferences', alias='$type', frozen=True
    )


class ReportRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`. Reference to a report by its report table ID, as used by getReport and Ozone's report detail page."""

    report_id: int  #: Report id.
    status: t.Optional[t.Union[t.Literal['pending', 'resolved'], str]] = None  #: Status.
    subject: t.Optional[
        unknown_union.OpenUnion[t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']]
    ] = None  #: Subject.

    py_type: t.Literal['tools.ozone.inbox.defs#reportRef'] = Field(
        default='tools.ozone.inbox.defs#reportRef', alias='$type', frozen=True
    )


class SubjectRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`."""

    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject.
    action_id: t.Optional[int] = None  #: Action id.
    action_type: t.Optional[str] = None  #: Action type.
    appeal_outcome: t.Optional[t.Union[t.Literal['approved', 'denied'], str]] = (
        None  #: Decision captured when an appealResolved notification was created. Omitted when the outcome is unknown.
    )

    py_type: t.Literal['tools.ozone.inbox.defs#subjectRef'] = Field(
        default='tools.ozone.inbox.defs#subjectRef', alias='$type', frozen=True
    )


class StandingRef(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.defs`."""

    standing: t.Union[t.Literal['good', 'warning', 'atRisk'], str]  #: Standing.
    previous_standing: t.Optional[t.Union[t.Literal['good', 'warning', 'atRisk'], str]] = None  #: Previous standing.

    py_type: t.Literal['tools.ozone.inbox.defs#standingRef'] = Field(
        default='tools.ozone.inbox.defs#standingRef', alias='$type', frozen=True
    )
