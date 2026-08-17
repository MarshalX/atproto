#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.video.abortUpload`."""

    job_id: str = Field(min_length=1, max_length=256)  #: Job id.


class DataDict(t.TypedDict):
    job_id: str  #: Job id.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.video.abortUpload`."""

    state: t.Union[t.Literal['aborted'], t.Literal['completed'], t.Literal['failed'], t.Literal['expired'], str] = (
        Field(max_length=32)
    )  #: State.
    completed_job_id: te.Annotated[t.Optional[str], Field(min_length=1, max_length=256)] = (
        None  #: Present only when state is completed.
    )
    failure_reason: te.Annotated[t.Optional[str], Field(max_length=1024)] = None  #: Present only when state is failed.
