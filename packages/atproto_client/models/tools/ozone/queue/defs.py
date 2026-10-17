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
from atproto_client.models import base


class QueueView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.queue.defs`."""

    created_at: string_formats.DateTime  #: Created at.
    created_by: string_formats.Did  #: DID of moderator who created this queue.
    enabled: bool  #: Whether this queue is currently active.
    id: int  #: Queue ID.
    name: str  #: Display name of the queue.
    stats: 'models.ToolsOzoneQueueDefs.QueueStats'  #: Statistics about this queue.
    updated_at: string_formats.DateTime  #: Updated at.
    collection: t.Optional[string_formats.Nsid] = (
        None  #: Collection name for record subjects (e.g., 'app.bsky.feed.post').
    )
    deleted_at: t.Optional[string_formats.DateTime] = None  #: When the queue was deleted, if applicable.
    description: t.Optional[str] = None  #: Optional description of the queue.
    recommended_labels: t.Optional[t.List[str]] = (
        None  #: Labels recommended for this queue and used as a fallback when routing label appeals.
    )
    recommended_policies: t.Optional[t.List[str]] = (
        None  #: Policy keys recommended when actioning reports in this queue.
    )
    report_types: t.Optional[t.List[str]] = None  #: Report reason types this queue accepts (fully qualified NSIDs).
    subject_types: t.Optional[t.List[t.Union[t.Literal['account', 'record', 'message', 'conversation'], str]]] = (
        None  #: Subject types this queue accepts.
    )

    py_type: t.Literal['tools.ozone.queue.defs#queueView'] = Field(
        default='tools.ozone.queue.defs#queueView', alias='$type', frozen=True
    )


class QueueStats(base.ModelBase):
    """Definition model for :obj:`tools.ozone.queue.defs`."""

    acknowledged_count: t.Optional[int] = (
        None  #: Number of closures whose last report action is not label, tag, or takedown.
    )
    action_rate: t.Optional[int] = (
        None  #: Percentage of closures actioned (actionedCount / closedCount * 100), rounded to nearest integer.
    )
    actioned_count: t.Optional[int] = None  #: Number of closures whose last report action is label, tag, or takedown.
    aht_duration_sec: t.Optional[int] = None  #: Sum of report assignment-to-close seconds.
    aht_sample_count: t.Optional[int] = None  #: Number of assigned closed-report samples in ahtDurationSec.
    avg_handling_time_sec: t.Optional[int] = None  #: Average handling time in seconds from report assignment to close.
    avg_resolution_time_sec: t.Optional[int] = (
        None  #: Average resolution time in seconds from report creation to close.
    )
    closed_count: t.Optional[int] = None  #: Number of reports whose current closure falls within this UTC calendar day.
    closure_target_met_count: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Reports whose closure meets their closure target.
    )
    closure_target_met_rate: te.Annotated[t.Optional[int], Field(ge=0, le=100)] = (
        None  #: Percent of reports meeting their closure target.
    )
    closure_target_missed_count: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Reports whose closure exceeds their closure target.
    )
    closure_target_overdue_count: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Unmuted pending reports past their closure target.
    )
    escalated_count: t.Optional[int] = None  #: Number of report escalation events during this UTC calendar day.
    inbound_count: t.Optional[int] = None  #: Reports received in this queue during this UTC calendar day.
    label_action_count: t.Optional[int] = None  #: Closures whose last report action is a label event.
    last_updated: t.Optional[string_formats.DateTime] = None  #: When these statistics were last computed.
    pending_count: t.Optional[int] = None  #: Number of unmuted reports currently not closed.
    resolution_duration_sec: t.Optional[int] = None  #: Sum of report creation-to-close seconds.
    resolution_sample_count: t.Optional[int] = None  #: Number of closed-report samples in resolutionDurationSec.
    tag_action_count: t.Optional[int] = None  #: Closures whose last report action is a tag event.
    takedown_action_count: t.Optional[int] = None  #: Closures whose last report action is a takedown event.

    py_type: t.Literal['tools.ozone.queue.defs#queueStats'] = Field(
        default='tools.ozone.queue.defs#queueStats', alias='$type', frozen=True
    )


class AssignmentView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.queue.defs`."""

    did: string_formats.Did  #: Did.
    id: int  #: Id.
    queue: 'models.ToolsOzoneQueueDefs.QueueView'  #: Queue.
    start_at: string_formats.DateTime  #: Start at.
    end_at: t.Optional[string_formats.DateTime] = None  #: End at.
    moderator: t.Optional['models.ToolsOzoneTeamDefs.Member'] = None  #: The moderator assigned to this queue.

    py_type: t.Literal['tools.ozone.queue.defs#assignmentView'] = Field(
        default='tools.ozone.queue.defs#assignmentView', alias='$type', frozen=True
    )
