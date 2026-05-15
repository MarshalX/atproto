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
    """Input data model for :obj:`tools.ozone.queue.createQueue`."""

    name: str  #: Display name for the queue (must be unique).
    report_types: t.List[str] = Field(min_length=1, max_length=25)  #: Report reason types (fully qualified NSIDs).
    subject_types: t.List[t.Union[t.Literal['account'], t.Literal['record'], t.Literal['message'], str]] = Field(
        min_length=1
    )  #: Subject types this queue accepts.
    collection: t.Optional[string_formats.Nsid] = (
        None  #: Collection name for record subjects. Required if subjectTypes includes 'record'.
    )
    description: t.Optional[str] = None  #: Optional description of the queue.


class DataDict(t.TypedDict):
    name: str  #: Display name for the queue (must be unique).
    report_types: t.List[str]  #: Report reason types (fully qualified NSIDs).
    subject_types: t.List[
        t.Union[t.Literal['account'], t.Literal['record'], t.Literal['message'], str]
    ]  #: Subject types this queue accepts.
    collection: te.NotRequired[
        t.Optional[string_formats.Nsid]
    ]  #: Collection name for record subjects. Required if subjectTypes includes 'record'.
    description: te.NotRequired[t.Optional[str]]  #: Optional description of the queue.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.createQueue`."""

    queue: 'models.ToolsOzoneQueueDefs.QueueView'  #: Queue.
