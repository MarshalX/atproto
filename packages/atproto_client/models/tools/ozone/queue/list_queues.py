##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.queue.listQueues`."""

    collection: t.Optional[str] = None  #: Filter queues by collection name (e.g. 'app.bsky.feed.post').
    cursor: t.Optional[str] = None  #: Cursor.
    enabled: t.Optional[bool] = None  #: Filter by enabled status. If not specified, returns all queues.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    report_types: te.Annotated[t.Optional[t.List[str]], Field(max_length=10)] = (
        None  #: Filter queues that handle any of these report reason types.
    )
    subject_type: t.Optional[str] = None  #: Filter queues that handle this subject type ('account' or 'record').


class ParamsDict(t.TypedDict):
    collection: te.NotRequired[t.Optional[str]]  #: Filter queues by collection name (e.g. 'app.bsky.feed.post').
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    enabled: te.NotRequired[t.Optional[bool]]  #: Filter by enabled status. If not specified, returns all queues.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    report_types: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Filter queues that handle any of these report reason types.
    subject_type: te.NotRequired[
        t.Optional[str]
    ]  #: Filter queues that handle this subject type ('account' or 'record').


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.listQueues`."""

    queues: t.List['models.ToolsOzoneQueueDefs.QueueView']  #: Queues.
    cursor: t.Optional[str] = None  #: Cursor.
