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


class Data(base.DataModelBase):
    """Input data model for :obj:`tools.ozone.queue.createQueue`."""

    name: str  #: Display name for the queue (must be unique).
    collection: t.Optional[string_formats.Nsid] = (
        None  #: Collection name for record subjects. Required if subjectTypes includes 'record'.
    )
    description: t.Optional[str] = None  #: Optional description of the queue.
    report_types: te.Annotated[t.Optional[t.List[str]], Field(max_length=25)] = (
        None  #: Report reason types (fully qualified NSIDs).
    )
    subject_types: t.Optional[
        t.List[t.Union[t.Literal['account'], t.Literal['record'], t.Literal['message'], t.Literal['conversation'], str]]
    ] = None  #: Subject types this queue accepts.


class DataDict(t.TypedDict):
    name: str  #: Display name for the queue (must be unique).
    collection: te.NotRequired[
        t.Optional[string_formats.Nsid]
    ]  #: Collection name for record subjects. Required if subjectTypes includes 'record'.
    description: te.NotRequired[t.Optional[str]]  #: Optional description of the queue.
    report_types: te.NotRequired[t.Optional[t.List[str]]]  #: Report reason types (fully qualified NSIDs).
    subject_types: te.NotRequired[
        t.Optional[
            t.List[
                t.Union[t.Literal['account'], t.Literal['record'], t.Literal['message'], t.Literal['conversation'], str]
            ]
        ]
    ]  #: Subject types this queue accepts.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.queue.createQueue`."""

    queue: 'models.ToolsOzoneQueueDefs.QueueView'  #: Queue.
