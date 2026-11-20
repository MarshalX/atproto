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


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.moderation.emitEvents`."""

    created_by: string_formats.Did  #: Created by.
    event: unknown_union.OpenUnion[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventTag',
            'models.ToolsOzoneModerationDefs.RevokeAccountCredentialsEvent',
        ]
    ]  #: Event.
    subjects: t.List['models.ToolsOzoneModerationEmitEvents.SubjectEntry'] = Field(
        max_length=100
    )  #: Array of subjects to apply the moderation event to.
    mod_tool: t.Optional['models.ToolsOzoneModerationDefs.ModTool'] = None  #: Mod tool.


class DataDict(t.TypedDict):
    created_by: string_formats.Did  #: Created by.
    event: unknown_union.OpenUnion[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventTag',
            'models.ToolsOzoneModerationDefs.RevokeAccountCredentialsEvent',
        ]
    ]  #: Event.
    subjects: t.List[
        'models.ToolsOzoneModerationEmitEvents.SubjectEntry'
    ]  #: Array of subjects to apply the moderation event to.
    mod_tool: te.NotRequired[t.Optional['models.ToolsOzoneModerationDefs.ModTool']]  #: Mod tool.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.moderation.emitEvents`."""

    events: t.List['models.ToolsOzoneModerationDefs.ModEventView']  #: Successfully processed moderation events.
    failed_events: t.List['models.ToolsOzoneModerationEmitEvents.FailedEvent']  #: Events that failed to process.


class SubjectEntry(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.emitEvents`. A subject with optional blob CIDs, external event ID, and report-level targeting. Report targeting applies only to this entry."""

    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: Subject.
    external_id: t.Optional[str] = None  #: Deduplicate events of this type for this subject using an external ID.
    report_action: t.Optional['models.ToolsOzoneModerationEmitEvent.ReportAction'] = (
        None  #: Optional report-level targeting for this subject. Links the event to matching reports and may notify reporters.
    )
    subject_blob_cids: t.Optional[t.List[string_formats.Cid]] = None  #: Subject blob cids.

    py_type: t.Literal['tools.ozone.moderation.emitEvents#subjectEntry'] = Field(
        default='tools.ozone.moderation.emitEvents#subjectEntry', alias='$type', frozen=True
    )


class FailedEvent(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.emitEvents`. An event that failed to process."""

    error: str  #: Error message describing the reason for failure.
    subject: unknown_union.OpenUnion[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main']
    ]  #: The subject from the failed event input.
    error_name: t.Optional[
        t.Union[
            t.Literal[
                'InvalidSubject',
                'SubjectHasAction',
                'AlreadyTakendown',
                'NotTakendown',
                'DuplicateExternalId',
                'InvalidConfiguration',
                'InvalidRequest',
            ],
            str,
        ]
    ] = None  #: Typed error identifier for programmatic handling. Omitted when the error is unexpected/uncategorized.

    py_type: t.Literal['tools.ozone.moderation.emitEvents#failedEvent'] = Field(
        default='tools.ozone.moderation.emitEvents#failedEvent', alias='$type', frozen=True
    )
