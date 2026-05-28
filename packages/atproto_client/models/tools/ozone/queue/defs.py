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


class QueueView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.queue.defs`."""

    created_at: string_formats.DateTime  #: Created at.
    created_by: string_formats.Did  #: DID of moderator who created this queue.
    enabled: bool  #: Whether this queue is currently active.
    id: int  #: Queue ID.
    name: str  #: Display name of the queue.
    report_types: t.List[str] = Field(min_length=1)  #: Report reason types this queue accepts (fully qualified NSIDs).
    stats: 'models.ToolsOzoneQueueDefs.QueueStats'  #: Statistics about this queue.
    subject_types: t.List[t.Union[t.Literal['account'], t.Literal['record'], t.Literal['message'], str]] = Field(
        min_length=1
    )  #: Subject types this queue accepts.
    updated_at: string_formats.DateTime  #: Updated at.
    collection: t.Optional[string_formats.Nsid] = (
        None  #: Collection name for record subjects (e.g., 'app.bsky.feed.post').
    )
    deleted_at: t.Optional[string_formats.DateTime] = None  #: When the queue was deleted, if applicable.
    description: t.Optional[str] = None  #: Optional description of the queue.

    py_type: t.Literal['tools.ozone.queue.defs#queueView'] = Field(
        default='tools.ozone.queue.defs#queueView', alias='$type', frozen=True
    )


class QueueStats(base.ModelBase):
    """Definition model for :obj:`tools.ozone.queue.defs`."""

    action_rate: t.Optional[int] = (
        None  #: Percentage of reports actioned (actionedCount / inboundCount * 100), rounded to nearest integer. Absent when inboundCount is 0.
    )
    actioned_count: t.Optional[int] = None  #: Number of reports in 'closed' status.
    avg_handling_time_sec: t.Optional[int] = (
        None  #: Average time in seconds from report creation to close, for reports closed in this period.
    )
    escalated_count: t.Optional[int] = None  #: Number of reports in 'escalated' status.
    inbound_count: t.Optional[int] = None  #: Reports received in this queue in the last 24 hours.
    last_updated: t.Optional[string_formats.DateTime] = None  #: When these statistics were last computed.
    pending_count: t.Optional[int] = None  #: Number of reports in 'open' status.

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
