#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`app.bsky.video.startUpload`."""

    mime_type: str = Field(min_length=3, max_length=255)  #: Declared MIME type of the video.
    size_bytes: int = Field(
        ge=1
    )  #: Exact byte size of the complete upload-ready video file before it is split into parts.
    duration_ms: t.Optional[int] = (
        None  #: Advisory, non-authoritative duration used only for early failure; the authoritative probe runs asynchronously after upload.
    )
    height: t.Optional[int] = (
        None  #: Advisory, non-authoritative height used only for early failure; the authoritative probe runs asynchronously after upload.
    )
    name: te.Annotated[t.Optional[str], Field(max_length=256)] = None  #: Optional client-provided file name.
    width: t.Optional[int] = (
        None  #: Advisory, non-authoritative width used only for early failure; the authoritative probe runs asynchronously after upload.
    )


class DataDict(t.TypedDict):
    mime_type: str  #: Declared MIME type of the video.
    size_bytes: int  #: Exact byte size of the complete upload-ready video file before it is split into parts.
    duration_ms: te.NotRequired[
        t.Optional[int]
    ]  #: Advisory, non-authoritative duration used only for early failure; the authoritative probe runs asynchronously after upload.
    height: te.NotRequired[
        t.Optional[int]
    ]  #: Advisory, non-authoritative height used only for early failure; the authoritative probe runs asynchronously after upload.
    name: te.NotRequired[t.Optional[str]]  #: Optional client-provided file name.
    width: te.NotRequired[
        t.Optional[int]
    ]  #: Advisory, non-authoritative width used only for early failure; the authoritative probe runs asynchronously after upload.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.video.startUpload`."""

    expires_at: string_formats.DateTime  #: Expires at.
    job_id: str = Field(min_length=1, max_length=256)  #: Job id.
    part_count: int  #: Part count.
    part_size_bytes: int  #: Part size bytes.
