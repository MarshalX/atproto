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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.moderation.getAccountTimeline`."""

    did: string_formats.Did  #: Did.


class ParamsDict(t.TypedDict):
    did: string_formats.Did  #: Did.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.moderation.getAccountTimeline`."""

    timeline: t.List['models.ToolsOzoneModerationGetAccountTimeline.TimelineItem']  #: Timeline.


class TimelineItem(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.getAccountTimeline`."""

    day: str  #: Day.
    summary: t.List['models.ToolsOzoneModerationGetAccountTimeline.TimelineItemSummary']  #: Summary.

    py_type: t.Literal['tools.ozone.moderation.getAccountTimeline#timelineItem'] = Field(
        default='tools.ozone.moderation.getAccountTimeline#timelineItem', alias='$type', frozen=True
    )


class TimelineItemSummary(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.getAccountTimeline`."""

    count: int  #: Count.
    event_subject_type: t.Union[t.Literal['account', 'record', 'chat'], str]  #: Event subject type.
    event_type: t.Union[
        t.Literal[
            'tools.ozone.moderation.defs#modEventTakedown',
            'tools.ozone.moderation.defs#modEventReverseTakedown',
            'tools.ozone.moderation.defs#modEventComment',
            'tools.ozone.moderation.defs#modEventReport',
            'tools.ozone.moderation.defs#modEventLabel',
            'tools.ozone.moderation.defs#modEventAcknowledge',
            'tools.ozone.moderation.defs#modEventEscalate',
            'tools.ozone.moderation.defs#modEventMute',
            'tools.ozone.moderation.defs#modEventUnmute',
            'tools.ozone.moderation.defs#modEventMuteReporter',
            'tools.ozone.moderation.defs#modEventUnmuteReporter',
            'tools.ozone.moderation.defs#modEventEmail',
            'tools.ozone.moderation.defs#modEventResolveAppeal',
            'tools.ozone.moderation.defs#modEventDivert',
            'tools.ozone.moderation.defs#modEventTag',
            'tools.ozone.moderation.defs#accountEvent',
            'tools.ozone.moderation.defs#identityEvent',
            'tools.ozone.moderation.defs#recordEvent',
            'tools.ozone.moderation.defs#modEventPriorityScore',
            'tools.ozone.moderation.defs#revokeAccountCredentialsEvent',
            'tools.ozone.moderation.defs#ageAssuranceEvent',
            'tools.ozone.moderation.defs#ageAssuranceOverrideEvent',
            'tools.ozone.hosting.getAccountHistory#accountCreated',
            'tools.ozone.hosting.getAccountHistory#emailConfirmed',
            'tools.ozone.hosting.getAccountHistory#passwordUpdated',
            'tools.ozone.hosting.getAccountHistory#handleUpdated',
            'tools.ozone.moderation.defs#scheduleTakedownEvent',
            'tools.ozone.moderation.defs#cancelScheduledTakedownEvent',
        ],
        'models.ToolsOzoneModerationDefs.TimelineEventPlcCreate',
        'models.ToolsOzoneModerationDefs.TimelineEventPlcOperation',
        'models.ToolsOzoneModerationDefs.TimelineEventPlcTombstone',
        str,
    ]  #: Event type.

    py_type: t.Literal['tools.ozone.moderation.getAccountTimeline#timelineItemSummary'] = Field(
        default='tools.ozone.moderation.getAccountTimeline#timelineItemSummary', alias='$type', frozen=True
    )
