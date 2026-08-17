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
    """Input data model for :obj:`network.bsky.jetstream.planSnapshot`."""

    after_seq: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Start after this sequence number. Events at or below it are not included.
    )
    before_seq: te.Annotated[t.Optional[int], Field(ge=0)] = (
        None  #: Stop at this sequence number. Events above it are not included.
    )
    collections: te.Annotated[t.Optional[t.List[str]], Field(max_length=100)] = (
        None  #: Collection NSIDs or namespace wildcards such as app.bsky.feed.*; constrains commit events only. Non-commit kinds are unaffected, so combine with kinds=commit for a commits-only collection plan. Rejected when kinds is set and excludes commit. Omit or pass an empty array to include all collections.
    )
    dids: te.Annotated[t.Optional[t.List[string_formats.Did]], Field(max_length=10000)] = (
        None  #: Only include data for these DIDs. Omit this field or pass an empty array to include all DIDs.
    )
    kinds: te.Annotated[t.Optional[t.List[t.Literal['commit', 'identity', 'account', 'sync']]], Field(max_length=4)] = (
        None  #: Event kinds to include. Omit this field or pass an empty array to include all kinds.
    )


class DataDict(t.TypedDict):
    after_seq: te.NotRequired[
        t.Optional[int]
    ]  #: Start after this sequence number. Events at or below it are not included.
    before_seq: te.NotRequired[t.Optional[int]]  #: Stop at this sequence number. Events above it are not included.
    collections: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Collection NSIDs or namespace wildcards such as app.bsky.feed.*; constrains commit events only. Non-commit kinds are unaffected, so combine with kinds=commit for a commits-only collection plan. Rejected when kinds is set and excludes commit. Omit or pass an empty array to include all collections.
    dids: te.NotRequired[
        t.Optional[t.List[string_formats.Did]]
    ]  #: Only include data for these DIDs. Omit this field or pass an empty array to include all DIDs.
    kinds: te.NotRequired[
        t.Optional[t.List[t.Literal['commit', 'identity', 'account', 'sync']]]
    ]  #: Event kinds to include. Omit this field or pass an empty array to include all kinds.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`network.bsky.jetstream.planSnapshot`."""

    planned_through_seq: int = Field(
        ge=0
    )  #: The last sealed sequence covered by this page. Use this value as afterSeq for the next page. If the response hits the server's page limit, this is the maxSeq of the last item returned; otherwise it equals sealedTipSeq. Planning is complete when plannedThroughSeq reaches sealedTipSeq.
    sealed_tip_seq: int = Field(
        ge=0
    )  #: The end of the sealed archive for this snapshot, capped by beforeSeq when provided. Use this value as beforeSeq on later pages so the snapshot does not move while it is being downloaded.
    segments: t.List['models.NetworkBskyJetstreamPlanSnapshot.Segment']  #: Segments.
    stats: 'models.NetworkBskyJetstreamPlanSnapshot.Stats'  #: Stats.


class Segment(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.planSnapshot`."""

    checksum: str = Field(
        min_length=16, max_length=16
    )  #: The segment's xxh3 metadata checksum, encoded as 16 hexadecimal characters.
    index: int = Field(ge=0)  #: Zero-based segment index.
    max_seq: int = Field(ge=0)  #: Max seq.
    min_seq: int = Field(ge=0)  #: Min seq.
    mode: t.Union[
        t.Literal['segment', 'blocks'], str
    ]  #: How to download this segment. For segment, download the whole file with getSegment. For blocks, download the ranges listed in blocks with getBlock.
    name: str  #: Segment filename to pass to getSegment or getBlock.
    blocks: t.Optional[t.List['models.NetworkBskyJetstreamPlanSnapshot.BlockRange']] = (
        None  #: Block ranges to download, including both endpoints. This field is present only when mode is blocks.
    )

    py_type: t.Literal['network.bsky.jetstream.planSnapshot#segment'] = Field(
        default='network.bsky.jetstream.planSnapshot#segment', alias='$type', frozen=True
    )


class BlockRange(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.planSnapshot`."""

    first: int = Field(ge=0)  #: Index of the first block in the range.
    last: int = Field(ge=0)  #: Index of the last block in the range.

    py_type: t.Literal['network.bsky.jetstream.planSnapshot#blockRange'] = Field(
        default='network.bsky.jetstream.planSnapshot#blockRange', alias='$type', frozen=True
    )


class Stats(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.planSnapshot`."""

    blocks_matched: int = Field(ge=0)  #: Blocks matched.
    entries: int = Field(ge=0)  #: Number of items counted toward the server's per-page plan limit.
    segments_examined: int = Field(ge=0)  #: Segments examined.
    segments_matched: int = Field(ge=0)  #: Segments matched.

    py_type: t.Literal['network.bsky.jetstream.planSnapshot#stats'] = Field(
        default='network.bsky.jetstream.planSnapshot#stats', alias='$type', frozen=True
    )
