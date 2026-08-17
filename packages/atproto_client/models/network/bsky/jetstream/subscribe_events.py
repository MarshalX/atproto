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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`network.bsky.jetstream.subscribeEvents`."""

    collections: te.Annotated[t.Optional[t.List[str]], Field(max_length=100)] = (
        None  #: Collection NSIDs or '<prefix>.*' patterns; constrains which commit events are delivered. Non-commit kinds are unaffected — combine with kinds=commit for a commits-only collection stream. Rejected pre-upgrade with HTTP 400 (InvalidRequest) when kinds is set and excludes commit, since the filter could never apply. Omitted or empty: all collections.
    )
    cursor: t.Optional[int] = (
        None  #: Resume position, inclusive: the server replays events with seq >= cursor and the client dedups the overlap. Values >= 1e15 are interpreted as a unix-microseconds timestamp instead of a seq and translated to the first seq witnessed at or after that instant; a timestamp below the retention floor clamps up to the floor and an #info OutdatedCursor frame is sent. Omitted: start at the live tip.
    )
    dids: te.Annotated[t.Optional[t.List[string_formats.Did]], Field(max_length=10000)] = (
        None  #: Repo DIDs to receive events for; applies to every event kind. Omitted or empty: all repos.
    )
    kinds: te.Annotated[t.Optional[t.List[t.Literal['commit', 'identity', 'account', 'sync']]], Field(max_length=4)] = (
        None  #: Event kinds to receive; values are the message $type fragment names. Omitted or empty: all kinds. A value outside the enum is rejected pre-upgrade with HTTP 400 (InvalidRequest) rather than silently never matching.
    )
    max_message_size_bytes: te.Annotated[t.Optional[int], Field(ge=0, le=4294967295)] = (
        None  #: Skip events whose uncompressed frame (envelope included) exceeds this many bytes. 0 (default) means no limit.
    )
    zstd_dictionary: te.Annotated[t.Optional[int], Field(ge=1)] = (
        None  #: Jetstream extension: opt into dict-zstd frame compression with the given zstd dictionary ID (obtained via network.bsky.jetstream.getZstdDictionary). Frames then arrive as binary websocket messages, each one zstd frame whose decompressed bytes are exactly the xrpc.v1.json text frame. An unknown or retired ID is rejected pre-upgrade with HTTP 400 carrying the current ID.
    )


class ParamsDict(t.TypedDict):
    collections: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Collection NSIDs or '<prefix>.*' patterns; constrains which commit events are delivered. Non-commit kinds are unaffected — combine with kinds=commit for a commits-only collection stream. Rejected pre-upgrade with HTTP 400 (InvalidRequest) when kinds is set and excludes commit, since the filter could never apply. Omitted or empty: all collections.
    cursor: te.NotRequired[
        t.Optional[int]
    ]  #: Resume position, inclusive: the server replays events with seq >= cursor and the client dedups the overlap. Values >= 1e15 are interpreted as a unix-microseconds timestamp instead of a seq and translated to the first seq witnessed at or after that instant; a timestamp below the retention floor clamps up to the floor and an #info OutdatedCursor frame is sent. Omitted: start at the live tip.
    dids: te.NotRequired[
        t.Optional[t.List[string_formats.Did]]
    ]  #: Repo DIDs to receive events for; applies to every event kind. Omitted or empty: all repos.
    kinds: te.NotRequired[
        t.Optional[t.List[t.Literal['commit', 'identity', 'account', 'sync']]]
    ]  #: Event kinds to receive; values are the message $type fragment names. Omitted or empty: all kinds. A value outside the enum is rejected pre-upgrade with HTTP 400 (InvalidRequest) rather than silently never matching.
    max_message_size_bytes: te.NotRequired[
        t.Optional[int]
    ]  #: Skip events whose uncompressed frame (envelope included) exceeds this many bytes. 0 (default) means no limit.
    zstd_dictionary: te.NotRequired[
        t.Optional[int]
    ]  #: Jetstream extension: opt into dict-zstd frame compression with the given zstd dictionary ID (obtained via network.bsky.jetstream.getZstdDictionary). Frames then arrive as binary websocket messages, each one zstd frame whose decompressed bytes are exactly the xrpc.v1.json text frame. An unknown or retired ID is rejected pre-upgrade with HTTP 400 carrying the current ID.


class Commit(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.subscribeEvents`. A single record mutation (create, update, or delete)."""

    collection: string_formats.Nsid  #: Collection NSID of the record.
    did: string_formats.Did  #: Did.
    operation: t.Union[t.Literal['create', 'update', 'delete'], str]  #: Operation.
    rev: string_formats.Tid  #: The repo rev of the commit that produced this op.
    rkey: string_formats.RecordKey  #: Record key.
    seq: int  #: Jetstream's monotonic per-event sequence number; the stream cursor.
    time: string_formats.DateTime  #: The event's display timestamp, microsecond precision: when Jetstream witnessed the event, unless an operator timestamp import overrode it. Timestamp cursors translate against the witnessed time, so after an import this value may not be a faithful resume position.
    cid: t.Optional[string_formats.Cid] = None  #: CID of the record. Absent for deletes.
    record: t.Optional['UnknownType'] = None  #: The record decoded to JSON. Absent for deletes.

    py_type: t.Literal['network.bsky.jetstream.subscribeEvents#commit'] = Field(
        default='network.bsky.jetstream.subscribeEvents#commit', alias='$type', frozen=True
    )


class Identity(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.subscribeEvents`. An identity change (handle or DID document update), wrapping the upstream firehose event verbatim."""

    did: string_formats.Did  #: Did.
    identity: 'models.ComAtprotoSyncSubscribeRepos.Identity'  #: The upstream event; its seq and time are the upstream relay's, not Jetstream's.
    seq: int  #: Seq.
    time: string_formats.DateTime  #: The time Jetstream witnessed this event, microsecond precision. Timestamp imports apply only to record (commit) events, so this is always the witnessed time.

    py_type: t.Literal['network.bsky.jetstream.subscribeEvents#identity'] = Field(
        default='network.bsky.jetstream.subscribeEvents#identity', alias='$type', frozen=True
    )


class Account(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.subscribeEvents`. An account status change (active/deactivated/deleted/...), wrapping the upstream firehose event verbatim."""

    account: 'models.ComAtprotoSyncSubscribeRepos.Account'  #: The upstream event; its seq and time are the upstream relay's, not Jetstream's.
    did: string_formats.Did  #: Did.
    seq: int  #: Seq.
    time: string_formats.DateTime  #: The time Jetstream witnessed this event, microsecond precision. Timestamp imports apply only to record (commit) events, so this is always the witnessed time.

    py_type: t.Literal['network.bsky.jetstream.subscribeEvents#account'] = Field(
        default='network.bsky.jetstream.subscribeEvents#account', alias='$type', frozen=True
    )


class Sync(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.subscribeEvents`. An archived #sync event (broken commit chain; consumers should resync the repo), wrapping the upstream firehose event verbatim. Never emitted on the legacy v1 /subscribe wire."""

    did: string_formats.Did  #: Did.
    seq: int  #: Seq.
    sync: 'models.ComAtprotoSyncSubscribeRepos.Sync'  #: The upstream event; its seq and time are the upstream relay's, not Jetstream's.
    time: string_formats.DateTime  #: The time Jetstream witnessed this event, microsecond precision. Timestamp imports apply only to record (commit) events, so this is always the witnessed time.

    py_type: t.Literal['network.bsky.jetstream.subscribeEvents#sync'] = Field(
        default='network.bsky.jetstream.subscribeEvents#sync', alias='$type', frozen=True
    )


class Info(base.ModelBase):
    """Definition model for :obj:`network.bsky.jetstream.subscribeEvents`. An advisory, non-fatal notice about the stream (mirrors com.atproto.sync.subscribeRepos#info). Carries no seq and does not advance the cursor. OutdatedCursor is sent as the first frame when a unix-microseconds timestamp cursor below the retention floor was clamped up to the floor; the message names the seq actually resumed from."""

    name: t.Union[t.Literal['OutdatedCursor'], str]  #: Name.
    message: t.Optional[str] = None  #: Message.

    py_type: t.Literal['network.bsky.jetstream.subscribeEvents#info'] = Field(
        default='network.bsky.jetstream.subscribeEvents#info', alias='$type', frozen=True
    )
