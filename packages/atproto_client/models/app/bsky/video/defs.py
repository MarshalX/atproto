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
    from atproto_client.models.blob_ref import BlobRef
from atproto_client.models import base


class JobStatus(base.ModelBase):
    """Definition model for :obj:`app.bsky.video.defs`."""

    did: string_formats.Did  #: Did.
    job_id: str  #: Job id.
    state: t.Union[
        t.Literal[
            'JOB_STATE_CREATED',
            'JOB_STATE_ENCODING',
            'JOB_STATE_ENCODED',
            'JOB_STATE_SCANNING',
            'JOB_STATE_SCANNED',
            'JOB_STATE_UPLOADING',
            'JOB_STATE_UPLOADED',
            'JOB_STATE_COMPLETED',
            'JOB_STATE_FAILED',
        ],
        str,
    ]  #: The state of the video processing job. All values not listed as a known value indicate that the job is in process.
    blob: t.Optional['BlobRef'] = None  #: Blob.
    error: t.Optional[str] = None  #: Error.
    failure_code: t.Optional[
        t.Union[
            t.Literal[
                'validation_failure',
                'encoding_failure',
                'pds_upload_failure',
                'pds_upload_unsupported_blob_size',
                'generic_failure',
            ],
            str,
        ]
    ] = None  #: A machine-readable code for why the video processing job failed.
    message: t.Optional[str] = None  #: Message.
    progress: te.Annotated[t.Optional[int], Field(ge=0, le=100)] = (
        None  #: Progress within the current processing state.
    )

    py_type: t.Literal['app.bsky.video.defs#jobStatus'] = Field(
        default='app.bsky.video.defs#jobStatus', alias='$type', frozen=True
    )
