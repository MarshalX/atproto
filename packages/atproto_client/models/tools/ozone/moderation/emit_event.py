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


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.moderation.emitEvent`."""

    created_by: string_formats.Did  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventUnmute',
            'models.ToolsOzoneModerationDefs.ModEventMuteReporter',
            'models.ToolsOzoneModerationDefs.ModEventUnmuteReporter',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventDivert',
            'models.ToolsOzoneModerationDefs.ModEventTag',
            'models.ToolsOzoneModerationDefs.AccountEvent',
            'models.ToolsOzoneModerationDefs.IdentityEvent',
            'models.ToolsOzoneModerationDefs.RecordEvent',
            'models.ToolsOzoneModerationDefs.ModEventPriorityScore',
            'models.ToolsOzoneModerationDefs.AgeAssuranceEvent',
            'models.ToolsOzoneModerationDefs.AgeAssuranceOverrideEvent',
            'models.ToolsOzoneModerationDefs.AgeAssurancePurgeEvent',
            'models.ToolsOzoneModerationDefs.RevokeAccountCredentialsEvent',
            'models.ToolsOzoneModerationDefs.ScheduleTakedownEvent',
            'models.ToolsOzoneModerationDefs.CancelScheduledTakedownEvent',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    external_id: t.Optional[str] = (
        None  #: An optional external ID for the event, used to deduplicate events from external systems. Fails when an event of same type with the same external ID exists for the same subject.
    )
    mod_tool: t.Optional['models.ToolsOzoneModerationDefs.ModTool'] = None  #: Mod tool.
    report_action: t.Optional['models.ToolsOzoneModerationEmitEvent.ReportAction'] = (
        None  #: Optional report-level targeting. If provided, this event will be linked to specific reports and reporters may be notified.
    )
    subject_blob_cids: t.Optional[t.List[string_formats.Cid]] = None  #: Subject blob cids.


class DataDict(t.TypedDict):
    created_by: string_formats.Did  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventUnmute',
            'models.ToolsOzoneModerationDefs.ModEventMuteReporter',
            'models.ToolsOzoneModerationDefs.ModEventUnmuteReporter',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventDivert',
            'models.ToolsOzoneModerationDefs.ModEventTag',
            'models.ToolsOzoneModerationDefs.AccountEvent',
            'models.ToolsOzoneModerationDefs.IdentityEvent',
            'models.ToolsOzoneModerationDefs.RecordEvent',
            'models.ToolsOzoneModerationDefs.ModEventPriorityScore',
            'models.ToolsOzoneModerationDefs.AgeAssuranceEvent',
            'models.ToolsOzoneModerationDefs.AgeAssuranceOverrideEvent',
            'models.ToolsOzoneModerationDefs.AgeAssurancePurgeEvent',
            'models.ToolsOzoneModerationDefs.RevokeAccountCredentialsEvent',
            'models.ToolsOzoneModerationDefs.ScheduleTakedownEvent',
            'models.ToolsOzoneModerationDefs.CancelScheduledTakedownEvent',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    external_id: te.NotRequired[
        t.Optional[str]
    ]  #: An optional external ID for the event, used to deduplicate events from external systems. Fails when an event of same type with the same external ID exists for the same subject.
    mod_tool: te.NotRequired[t.Optional['models.ToolsOzoneModerationDefs.ModTool']]  #: Mod tool.
    report_action: te.NotRequired[
        t.Optional['models.ToolsOzoneModerationEmitEvent.ReportAction']
    ]  #: Optional report-level targeting. If provided, this event will be linked to specific reports and reporters may be notified.
    subject_blob_cids: te.NotRequired[t.Optional[t.List[string_formats.Cid]]]  #: Subject blob cids.


class ReportAction(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.emitEvent`. Target specific reports when emitting a moderation event."""

    all: t.Optional[bool] = None  #: Target ALL reports on the subject.
    ids: t.Optional[t.List[int]] = None  #: Target specific report IDs.
    note: t.Optional[str] = None  #: Note to send to reporter(s) when actioning their report.
    types: t.Optional[t.List[str]] = (
        None  #: Target reports matching these report types on the subject (fully qualified NSIDs).
    )

    py_type: t.Literal['tools.ozone.moderation.emitEvent#reportAction'] = Field(
        default='tools.ozone.moderation.emitEvent#reportAction', alias='$type', frozen=True
    )
