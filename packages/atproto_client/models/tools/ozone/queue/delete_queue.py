##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.deleteQueue`."""

    queue_id: int  #: ID of the queue to delete.
    migrate_to_queue_id: t.Optional[int] = (
        None  #: Optional: migrate all reports to this queue. If not specified, reports will be set to unassigned (-1).
    )


class DataDict(t.TypedDict):
    queue_id: int  #: ID of the queue to delete.
    migrate_to_queue_id: te.NotRequired[
        t.Optional[int]
    ]  #: Optional: migrate all reports to this queue. If not specified, reports will be set to unassigned (-1).


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.deleteQueue`."""

    deleted: bool  #: Deleted.
    reports_migrated: t.Optional[int] = None  #: Number of reports that were migrated (if migration occurred).
