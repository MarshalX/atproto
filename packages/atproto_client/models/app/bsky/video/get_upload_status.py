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


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.video.getUploadStatus`."""

    job_id: str = Field(min_length=1, max_length=256)  #: Job id.


class ParamsDict(t.TypedDict):
    job_id: str  #: Job id.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.video.getUploadStatus`."""

    expires_at: string_formats.DateTime  #: Expires at.
    job_id: str = Field(min_length=1, max_length=256)  #: Job id.
    part_count: int  #: Part count.
    part_size_bytes: int  #: Part size bytes.
    received_parts: t.List[te.Annotated[int, Field(ge=1)]]  #: Received parts.
    state: t.Union[t.Literal['created', 'finishing', 'completed', 'failed', 'aborted', 'expired'], str] = Field(
        max_length=32
    )  #: State.
    completed_job_id: te.Annotated[t.Optional[str], Field(min_length=1, max_length=256)] = (
        None  #: Present only when state is completed; may differ from jobId on deduplication.
    )
    failure_reason: te.Annotated[t.Optional[str], Field(max_length=1024)] = None  #: Present only when state is failed.
    job_status: t.Optional['models.AppBskyVideoDefs.JobStatus'] = None  #: Present only when state is completed.
