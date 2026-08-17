#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`network.bsky.jetstream.listSegments`."""

    cursor: t.Optional[str] = None  #: Opaque pagination cursor from a previous response.
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=1000)] = (
        None  #: Maximum number of segment file names to return.
    )


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Opaque pagination cursor from a previous response.
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of segment file names to return.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`network.bsky.jetstream.listSegments`."""

    segments: t.List['models.NetworkBskyJetstreamListSegments.Segment']  #: Segments.
    cursor: t.Optional[str] = None  #: Cursor.


class Segment(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.listSegments`."""

    checksum: str  #: Segment-format xxh3 metadata checksum as 16-char hex; equals the getSegment ETag.
    event_count: int  #: Number of events in the segment.
    index: int  #: Zero-based segment index.
    max_seq: int  #: Max seq.
    max_witnessed_at: int  #: Latest witnessed-at, unix microseconds.
    min_seq: int  #: Min seq.
    min_witnessed_at: int  #: Earliest witnessed-at, unix microseconds.
    name: str  #: Segment filename; pass to getSegment.
    size_bytes: int  #: File size in bytes.

    py_type: t.Literal['network.bsky.jetstream.listSegments#segment'] = Field(
        default='network.bsky.jetstream.listSegments#segment', alias='$type', frozen=True
    )
