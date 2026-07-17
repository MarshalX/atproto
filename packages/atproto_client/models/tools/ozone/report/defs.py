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
from atproto_client.models import base

ReasonType = t.Union[
    'models.ToolsOzoneReportDefs.ReasonAppeal',
    'models.ToolsOzoneReportDefs.ReasonOther',
    'models.ToolsOzoneReportDefs.ReasonViolenceAnimal',
    'models.ToolsOzoneReportDefs.ReasonViolenceThreats',
    'models.ToolsOzoneReportDefs.ReasonViolenceGraphicContent',
    'models.ToolsOzoneReportDefs.ReasonViolenceGlorification',
    'models.ToolsOzoneReportDefs.ReasonViolenceExtremistContent',
    'models.ToolsOzoneReportDefs.ReasonViolenceTrafficking',
    'models.ToolsOzoneReportDefs.ReasonViolenceOther',
    'models.ToolsOzoneReportDefs.ReasonSexualAbuseContent',
    'models.ToolsOzoneReportDefs.ReasonSexualNCII',
    'models.ToolsOzoneReportDefs.ReasonSexualDeepfake',
    'models.ToolsOzoneReportDefs.ReasonSexualAnimal',
    'models.ToolsOzoneReportDefs.ReasonSexualUnlabeled',
    'models.ToolsOzoneReportDefs.ReasonSexualOther',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyCSAM',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyGroom',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyPrivacy',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyHarassment',
    'models.ToolsOzoneReportDefs.ReasonChildSafetyOther',
    'models.ToolsOzoneReportDefs.ReasonHarassmentTroll',
    'models.ToolsOzoneReportDefs.ReasonHarassmentTargeted',
    'models.ToolsOzoneReportDefs.ReasonHarassmentHateSpeech',
    'models.ToolsOzoneReportDefs.ReasonHarassmentDoxxing',
    'models.ToolsOzoneReportDefs.ReasonHarassmentOther',
    'models.ToolsOzoneReportDefs.ReasonMisleadingBot',
    'models.ToolsOzoneReportDefs.ReasonMisleadingImpersonation',
    'models.ToolsOzoneReportDefs.ReasonMisleadingSpam',
    'models.ToolsOzoneReportDefs.ReasonMisleadingScam',
    'models.ToolsOzoneReportDefs.ReasonMisleadingElections',
    'models.ToolsOzoneReportDefs.ReasonMisleadingOther',
    'models.ToolsOzoneReportDefs.ReasonRuleSiteSecurity',
    'models.ToolsOzoneReportDefs.ReasonRuleProhibitedSales',
    'models.ToolsOzoneReportDefs.ReasonRuleBanEvasion',
    'models.ToolsOzoneReportDefs.ReasonRuleOther',
    'models.ToolsOzoneReportDefs.ReasonSelfHarmContent',
    'models.ToolsOzoneReportDefs.ReasonSelfHarmED',
    'models.ToolsOzoneReportDefs.ReasonSelfHarmStunts',
    'models.ToolsOzoneReportDefs.ReasonSelfHarmSubstances',
    'models.ToolsOzoneReportDefs.ReasonSelfHarmOther',
    str,
]  #: Reason type

ReasonAppeal = t.Literal['tools.ozone.report.defs#reasonAppeal']  #: Appeal a previously taken moderation action

ReasonOther = t.Literal['tools.ozone.report.defs#reasonOther']  #: An issue not included in these options

ReasonViolenceAnimal = t.Literal['tools.ozone.report.defs#reasonViolenceAnimal']  #: Animal welfare violations

ReasonViolenceThreats = t.Literal['tools.ozone.report.defs#reasonViolenceThreats']  #: Threats or incitement

ReasonViolenceGraphicContent = t.Literal[
    'tools.ozone.report.defs#reasonViolenceGraphicContent'
]  #: Graphic violent content

ReasonViolenceGlorification = t.Literal[
    'tools.ozone.report.defs#reasonViolenceGlorification'
]  #: Glorification of violence

ReasonViolenceExtremistContent = t.Literal[
    'tools.ozone.report.defs#reasonViolenceExtremistContent'
]  #: Extremist content. These reports will be sent only be sent to the application's Moderation Authority.

ReasonViolenceTrafficking = t.Literal['tools.ozone.report.defs#reasonViolenceTrafficking']  #: Human trafficking

ReasonViolenceOther = t.Literal['tools.ozone.report.defs#reasonViolenceOther']  #: Other violent content

ReasonSexualAbuseContent = t.Literal['tools.ozone.report.defs#reasonSexualAbuseContent']  #: Adult sexual abuse content

ReasonSexualNCII = t.Literal['tools.ozone.report.defs#reasonSexualNCII']  #: Non-consensual intimate imagery

ReasonSexualDeepfake = t.Literal['tools.ozone.report.defs#reasonSexualDeepfake']  #: Deepfake adult content

ReasonSexualAnimal = t.Literal['tools.ozone.report.defs#reasonSexualAnimal']  #: Animal sexual abuse

ReasonSexualUnlabeled = t.Literal['tools.ozone.report.defs#reasonSexualUnlabeled']  #: Unlabelled adult content

ReasonSexualOther = t.Literal['tools.ozone.report.defs#reasonSexualOther']  #: Other sexual violence content

ReasonChildSafetyCSAM = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyCSAM'
]  #: Child sexual abuse material (CSAM). These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyGroom = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyGroom'
]  #: Grooming or predatory behavior. These reports will be sent only be sent to the application's Moderation Authority.

ReasonChildSafetyPrivacy = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyPrivacy'
]  #: Privacy violation involving a minor

ReasonChildSafetyHarassment = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyHarassment'
]  #: Harassment or bullying of minors

ReasonChildSafetyOther = t.Literal[
    'tools.ozone.report.defs#reasonChildSafetyOther'
]  #: Other child safety. These reports will be sent only be sent to the application's Moderation Authority.

ReasonHarassmentTroll = t.Literal['tools.ozone.report.defs#reasonHarassmentTroll']  #: Trolling

ReasonHarassmentTargeted = t.Literal['tools.ozone.report.defs#reasonHarassmentTargeted']  #: Targeted harassment

ReasonHarassmentHateSpeech = t.Literal['tools.ozone.report.defs#reasonHarassmentHateSpeech']  #: Hate speech

ReasonHarassmentDoxxing = t.Literal['tools.ozone.report.defs#reasonHarassmentDoxxing']  #: Doxxing

ReasonHarassmentOther = t.Literal[
    'tools.ozone.report.defs#reasonHarassmentOther'
]  #: Other harassing or hateful content

ReasonMisleadingBot = t.Literal['tools.ozone.report.defs#reasonMisleadingBot']  #: Fake account or bot

ReasonMisleadingImpersonation = t.Literal['tools.ozone.report.defs#reasonMisleadingImpersonation']  #: Impersonation

ReasonMisleadingSpam = t.Literal['tools.ozone.report.defs#reasonMisleadingSpam']  #: Spam

ReasonMisleadingScam = t.Literal['tools.ozone.report.defs#reasonMisleadingScam']  #: Scam

ReasonMisleadingElections = t.Literal[
    'tools.ozone.report.defs#reasonMisleadingElections'
]  #: False information about elections

ReasonMisleadingOther = t.Literal['tools.ozone.report.defs#reasonMisleadingOther']  #: Other misleading content

ReasonRuleSiteSecurity = t.Literal['tools.ozone.report.defs#reasonRuleSiteSecurity']  #: Hacking or system attacks

ReasonRuleProhibitedSales = t.Literal[
    'tools.ozone.report.defs#reasonRuleProhibitedSales'
]  #: Promoting or selling prohibited items or services

ReasonRuleBanEvasion = t.Literal['tools.ozone.report.defs#reasonRuleBanEvasion']  #: Banned user returning

ReasonRuleOther = t.Literal['tools.ozone.report.defs#reasonRuleOther']  #: Other

ReasonSelfHarmContent = t.Literal[
    'tools.ozone.report.defs#reasonSelfHarmContent'
]  #: Content promoting or depicting self-harm

ReasonSelfHarmED = t.Literal['tools.ozone.report.defs#reasonSelfHarmED']  #: Eating disorders

ReasonSelfHarmStunts = t.Literal['tools.ozone.report.defs#reasonSelfHarmStunts']  #: Dangerous challenges or activities

ReasonSelfHarmSubstances = t.Literal[
    'tools.ozone.report.defs#reasonSelfHarmSubstances'
]  #: Dangerous substances or drug abuse

ReasonSelfHarmOther = t.Literal['tools.ozone.report.defs#reasonSelfHarmOther']  #: Other dangerous content


class ReportAssignment(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Information about the moderator currently assigned to a report."""

    assigned_at: string_formats.DateTime  #: When the report was assigned.
    did: string_formats.Did  #: DID of the assigned moderator.
    moderator: t.Optional['models.ToolsOzoneTeamDefs.Member'] = None  #: Full member record of the assigned moderator.

    py_type: t.Literal['tools.ozone.report.defs#reportAssignment'] = Field(
        default='tools.ozone.report.defs#reportAssignment', alias='$type', frozen=True
    )


class ReportView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`."""

    created_at: string_formats.DateTime  #: When the report was created.
    event_id: int  #: ID of the moderation event that created this report.
    id: int  #: Report ID.
    report_type: 'models.ComAtprotoModerationDefs.ReasonType'  #: Type of report.
    reported_by: string_formats.Did  #: DID of the user who made the report.
    reporter: 'models.ToolsOzoneModerationDefs.SubjectView'  #: Full subject view of the reporter account.
    status: t.Union[
        t.Literal['open'], t.Literal['closed'], t.Literal['escalated'], t.Literal['queued'], t.Literal['assigned'], str
    ]  #: Current status of the report.
    subject: 'models.ToolsOzoneModerationDefs.SubjectView'  #: The subject that was reported with full details.
    action_event_ids: t.Optional[t.List[int]] = (
        None  #: Array of moderation event IDs representing actions taken on this report (sorted DESC, most recent first).
    )
    action_note: t.Optional[str] = None  #: Note sent to reporter when report was actioned.
    actions: t.Optional[t.List['models.ToolsOzoneModerationDefs.ModEventView']] = (
        None  #: Optional: expanded action events.
    )
    assignment: t.Optional['models.ToolsOzoneReportDefs.ReportAssignment'] = (
        None  #: Information about moderator currently assigned to this report (if any).
    )
    comment: t.Optional[str] = None  #: Comment provided by the reporter.
    is_automated: t.Optional[bool] = False  #: Whether this report was emitted by automated tooling.
    is_muted: t.Optional[bool] = (
        None  #: Whether this report is muted. A report is muted if the reporter was muted or the subject was muted at the time the report was created.
    )
    queue: t.Optional['models.ToolsOzoneQueueDefs.QueueView'] = None  #: The queue this report is assigned to (if any).
    queued_at: t.Optional[string_formats.DateTime] = None  #: When the report was assigned to its current queue.
    related_report_count: t.Optional[int] = None  #: Number of other pending reports on the same subject.
    subject_status: t.Optional['models.ToolsOzoneModerationDefs.SubjectStatusView'] = (
        None  #: Current status of the reported subject.
    )
    updated_at: t.Optional[string_formats.DateTime] = None  #: When the report was last updated.

    py_type: t.Literal['tools.ozone.report.defs#reportView'] = Field(
        default='tools.ozone.report.defs#reportView', alias='$type', frozen=True
    )


class QueueActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a report being routed to a queue."""

    previous_status: t.Optional[
        t.Union[
            t.Literal['open'],
            t.Literal['closed'],
            t.Literal['escalated'],
            t.Literal['queued'],
            t.Literal['assigned'],
            str,
        ]
    ] = None  #: The report's status before this activity. Populated automatically from the report row; not required in input.

    py_type: t.Literal['tools.ozone.report.defs#queueActivity'] = Field(
        default='tools.ozone.report.defs#queueActivity', alias='$type', frozen=True
    )


class AssignmentActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a moderator being assigned to a report."""

    previous_status: t.Optional[
        t.Union[
            t.Literal['open'],
            t.Literal['closed'],
            t.Literal['escalated'],
            t.Literal['queued'],
            t.Literal['assigned'],
            str,
        ]
    ] = None  #: The report's status before this activity. Populated automatically from the report row; not required in input.

    py_type: t.Literal['tools.ozone.report.defs#assignmentActivity'] = Field(
        default='tools.ozone.report.defs#assignmentActivity', alias='$type', frozen=True
    )


class EscalationActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a report being escalated."""

    previous_status: t.Optional[
        t.Union[
            t.Literal['open'],
            t.Literal['closed'],
            t.Literal['escalated'],
            t.Literal['queued'],
            t.Literal['assigned'],
            str,
        ]
    ] = None  #: The report's status before this activity. Populated automatically from the report row; not required in input.

    py_type: t.Literal['tools.ozone.report.defs#escalationActivity'] = Field(
        default='tools.ozone.report.defs#escalationActivity', alias='$type', frozen=True
    )


class CloseActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a report being closed."""

    previous_status: t.Optional[
        t.Union[
            t.Literal['open'],
            t.Literal['closed'],
            t.Literal['escalated'],
            t.Literal['queued'],
            t.Literal['assigned'],
            str,
        ]
    ] = None  #: The report's status before this activity. Populated automatically from the report row; not required in input.

    py_type: t.Literal['tools.ozone.report.defs#closeActivity'] = Field(
        default='tools.ozone.report.defs#closeActivity', alias='$type', frozen=True
    )


class ReopenActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a closed report being reopened. Only valid when the report is in 'closed' status."""

    previous_status: t.Optional[
        t.Union[
            t.Literal['open'],
            t.Literal['closed'],
            t.Literal['escalated'],
            t.Literal['queued'],
            t.Literal['assigned'],
            str,
        ]
    ] = None  #: The report's status before this activity. Populated automatically from the report row; not required in input.

    py_type: t.Literal['tools.ozone.report.defs#reopenActivity'] = Field(
        default='tools.ozone.report.defs#reopenActivity', alias='$type', frozen=True
    )


class NoteActivity(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Activity recording a note on a report. Use internalNote for moderator-only notes or publicNote for reporter-visible notes (or both)."""

    py_type: t.Literal['tools.ozone.report.defs#noteActivity'] = Field(
        default='tools.ozone.report.defs#noteActivity', alias='$type', frozen=True
    )


class ReportActivityView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. A single activity entry on a report."""

    activity: te.Annotated[
        t.Union[
            'models.ToolsOzoneReportDefs.QueueActivity',
            'models.ToolsOzoneReportDefs.AssignmentActivity',
            'models.ToolsOzoneReportDefs.EscalationActivity',
            'models.ToolsOzoneReportDefs.CloseActivity',
            'models.ToolsOzoneReportDefs.ReopenActivity',
            'models.ToolsOzoneReportDefs.NoteActivity',
        ],
        Field(discriminator='py_type'),
    ]  #: The typed activity object describing what occurred.
    created_at: string_formats.DateTime  #: When this activity was created.
    created_by: (
        string_formats.Did
    )  #: DID of the actor who created this activity, or the service DID for automated activities.
    id: int  #: Activity ID.
    is_automated: bool  #: True if this activity was created by an automated process (e.g. queue router) rather than a direct human action.
    report_id: int  #: ID of the report this activity belongs to.
    internal_note: t.Optional[str] = None  #: Optional moderator-only note. Not visible to reporters.
    meta: t.Optional['UnknownType'] = (
        None  #: Extensible JSON payload for loose activity-specific metadata (e.g. assignmentId).
    )
    moderator: t.Optional['models.ToolsOzoneTeamDefs.Member'] = (
        None  #: Full member record of the moderator who created this activity.
    )
    public_note: t.Optional[str] = None  #: Optional public note, potentially visible to the reporter.
    report: t.Optional['models.ToolsOzoneReportDefs.ReportView'] = (
        None  #: Full view of the report this activity belongs to.
    )

    py_type: t.Literal['tools.ozone.report.defs#reportActivityView'] = Field(
        default='tools.ozone.report.defs#reportActivityView', alias='$type', frozen=True
    )


class LiveStats(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. Live statistics for reports for the current calendar day, filterable by queue, moderator, or report type."""

    action_rate: t.Optional[int] = (
        None  #: Percentage of reports actioned (actionedCount / inboundCount * 100), rounded to nearest integer.
    )
    actioned_count: t.Optional[int] = None  #: Number of reports closed today.
    avg_handling_time_sec: t.Optional[int] = (
        None  #: Average time in seconds from report creation (or moderator assignment) to close.
    )
    escalated_count: t.Optional[int] = None  #: Number of reports escalated today.
    inbound_count: t.Optional[int] = None  #: Reports received today.
    last_updated: t.Optional[string_formats.DateTime] = None  #: When these statistics were last computed.
    pending_count: t.Optional[int] = None  #: Number of reports currently not closed.

    py_type: t.Literal['tools.ozone.report.defs#liveStats'] = Field(
        default='tools.ozone.report.defs#liveStats', alias='$type', frozen=True
    )


class HistoricalStats(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`. A single daily snapshot of report statistics for a calendar date."""

    date: str  #: The calendar date this snapshot covers (YYYY-MM-DD).
    action_rate: t.Optional[int] = (
        None  #: Percentage of reports actioned (actionedCount / inboundCount * 100), rounded to nearest integer.
    )
    actioned_count: t.Optional[int] = None  #: Number of reports closed during this day.
    avg_handling_time_sec: t.Optional[int] = (
        None  #: Average time in seconds from report creation (or moderator assignment) to close.
    )
    computed_at: t.Optional[string_formats.DateTime] = None  #: When this snapshot was last computed.
    escalated_count: t.Optional[int] = None  #: Number of reports escalated during this day.
    inbound_count: t.Optional[int] = None  #: Reports received during this day.
    pending_count: t.Optional[int] = None  #: Number of reports not closed at time of computation.

    py_type: t.Literal['tools.ozone.report.defs#historicalStats'] = Field(
        default='tools.ozone.report.defs#historicalStats', alias='$type', frozen=True
    )


class AssignmentView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.report.defs`."""

    did: string_formats.Did  #: Did.
    id: int  #: Id.
    report_id: int  #: Report id.
    start_at: string_formats.DateTime  #: Start at.
    end_at: t.Optional[string_formats.DateTime] = None  #: End at.
    moderator: t.Optional['models.ToolsOzoneTeamDefs.Member'] = None  #: The moderator assigned to this report.
    queue: t.Optional['models.ToolsOzoneQueueDefs.QueueView'] = None  #: Queue.

    py_type: t.Literal['tools.ozone.report.defs#assignmentView'] = Field(
        default='tools.ozone.report.defs#assignmentView', alias='$type', frozen=True
    )
