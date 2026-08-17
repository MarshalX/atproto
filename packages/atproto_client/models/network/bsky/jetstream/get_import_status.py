#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`network.bsky.jetstream.getImportStatus`."""

    job: t.Optional[str] = (
        None  #: Job id returned by importTimestamps. When omitted, the current or most recent job is reported.
    )


class ParamsDict(t.TypedDict):
    job: te.NotRequired[
        t.Optional[str]
    ]  #: Job id returned by importTimestamps. When omitted, the current or most recent job is reported.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`network.bsky.jetstream.getImportStatus`."""

    job: str  #: Job id.
    state: t.Union[t.Literal['running', 'complete', 'failed'], str]  #: Lifecycle state.
    bucketed: t.Optional[bool] = None  #: Whether Phase A+B completed (the offset files are durable).
    error: t.Optional[str] = None  #: Failure detail; present only when state is failed.
    finished_at: t.Optional[string_formats.DateTime] = None  #: Present only for a terminal job.
    phase: t.Optional[t.Union[t.Literal['parse_bucket', 'apply'], str]] = (
        None  #: Current phase: parse_bucket (Phase A+B) or apply (Phase C).
    )
    rows_corrupt_offset: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows corrupt offset.
    rows_matched_all_versions: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows matched all versions.
    rows_matched_specific: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows matched specific.
    rows_mutated: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows mutated.
    rows_rejected: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows rejected.
    rows_total: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows total.
    rows_valid: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Rows valid.
    segments_applied: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Segments processed so far in Phase C.
    segments_examined: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Segments examined.
    segments_patched: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Segments patched.
    segments_to_apply: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Segments Phase C will process (after resume-skips).
    )
    specific_cids_unmatched: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Specific cids unmatched.
    submitted_at: t.Optional[string_formats.DateTime] = None  #: Submitted at.
