#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.video.finishUpload`."""

    job_id: str = Field(min_length=1, max_length=256)  #: Job id.


class DataDict(t.TypedDict):
    job_id: str  #: Job id.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.video.finishUpload`."""

    completed_job_id: str = Field(
        min_length=1, max_length=256
    )  #: The processing job to poll with getJobStatus; on deduplication this may differ from the input jobId.
    job_status: 'models.AppBskyVideoDefs.JobStatus'  #: Job status.
