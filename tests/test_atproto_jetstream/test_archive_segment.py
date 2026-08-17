"""Decoding of the `.jss` block format, and the exact row matcher.

Blocks are built in memory by ``block_writer`` rather than loaded from a fixture.
"""

import typing as t

import libipld
import pytest
import zstandard
from atproto_jetstream.archive.matcher import RowMatcher
from atproto_jetstream.archive.segment import (
    KIND_ACCOUNT,
    KIND_CREATE,
    KIND_DELETE,
    KIND_IDENTITY,
    KIND_SYNC,
    KIND_UPDATE,
    SegmentEvent,
    decode_block,
    decompress_block,
    read_sealed_header,
)
from atproto_jetstream.exceptions import JetstreamDecodingError

from .block_writer import encode_block, encode_columns


def make_event(
    seq: int,
    kind: int = KIND_CREATE,
    did: str = 'did:plc:aaa',
    collection: str = 'app.bsky.feed.post',
    rkey: str = '3l3qo2vuowo2b',
    rev: str = '3l3qo2vutsw2b',
    indexed_at: int = 0,
) -> SegmentEvent:
    """Build one row. Non-commit kinds carry empty record identity, as the format does."""
    is_commit = kind in (KIND_CREATE, KIND_UPDATE, KIND_DELETE)
    payload = None
    if kind != KIND_DELETE:
        payload = libipld.encode_dag_cbor({'$type': collection, 'text': f'row {seq}'})

    return SegmentEvent(
        seq=seq,
        witnessed_at=1_785_871_804_982_691,
        indexed_at=indexed_at,
        kind=kind,
        did=did,
        collection=collection if is_commit else '',
        rkey=rkey if is_commit else '',
        rev=rev if is_commit else '',
        payload=payload,
    )


#: Deliberately varied: differing field widths per row are what break an offset walk.
VARIED_ROWS = [
    make_event(10, collection='app.bsky.feed.post', rkey='self', did='did:plc:aaa'),
    make_event(11, collection='chat.bsky.actor.declaration', did='did:plc:bbbbbbbb'),
    make_event(12, kind=KIND_DELETE, collection='app.bsky.feed.like', did='did:plc:aaa'),
    make_event(13, kind=KIND_IDENTITY, did='did:plc:cccccccccccc'),
    make_event(14, kind=KIND_ACCOUNT, did='did:plc:aaa'),
    make_event(15, kind=KIND_SYNC, did='did:plc:bbbbbbbb'),
    make_event(16, kind=KIND_UPDATE, collection='app.bsky.graph.follow', rkey='3l3', did='did:plc:aaa'),
]


@pytest.fixture(scope='module')
def events() -> t.List[SegmentEvent]:
    return decode_block(encode_block(VARIED_ROWS))


def test_block_decompresses() -> None:
    assert decompress_block(encode_block(VARIED_ROWS)) == encode_columns(VARIED_ROWS)


def test_every_row_survives_the_round_trip(events: t.List[SegmentEvent]) -> None:
    # a wrong width or a slipped offset corrupts later rows rather than dropping them
    assert events == VARIED_ROWS


def test_decode_rejects_trailing_bytes() -> None:
    frame = zstandard.ZstdCompressor().compress(encode_columns(VARIED_ROWS) + b'\x00')

    with pytest.raises(JetstreamDecodingError, match='trailing'):
        decode_block(frame)


def test_decode_rejects_a_truncated_block() -> None:
    body = encode_columns(VARIED_ROWS)
    frame = zstandard.ZstdCompressor().compress(body[: len(body) // 2])

    with pytest.raises(JetstreamDecodingError):
        decode_block(frame)


def test_empty_block_decodes_to_nothing() -> None:
    assert decode_block(encode_block([])) == []


def test_single_row_block_decodes() -> None:
    assert decode_block(encode_block(VARIED_ROWS[:1])) == VARIED_ROWS[:1]


def test_commit_rows_carry_record_identity(events: t.List[SegmentEvent]) -> None:
    for event in events:
        if event.is_commit:
            assert event.collection and event.rkey and event.rev
            assert event.operation in ('create', 'update', 'delete')
        else:
            assert event.collection == '' and event.rkey == '' and event.rev == ''
            assert event.operation is None


def test_only_deletes_lack_a_payload(events: t.List[SegmentEvent]) -> None:
    assert any(event.kind == KIND_DELETE for event in events)

    for event in events:
        assert (event.payload is None) == (event.kind == KIND_DELETE)


def test_record_payloads_are_dag_cbor(events: t.List[SegmentEvent]) -> None:
    creates = [event for event in events if event.kind == KIND_CREATE]

    assert creates
    for event in creates:
        assert event.payload is not None
        assert libipld.decode_dag_cbor(event.payload)['$type'] == event.collection


def test_time_us_prefers_indexed_at() -> None:
    witnessed = decode_block(encode_block([make_event(1, indexed_at=0)]))[0]
    imported = decode_block(encode_block([make_event(1, indexed_at=42)]))[0]

    # indexed_at is only set by an operator timestamp import; 0 means fall back
    assert witnessed.time_us == witnessed.witnessed_at
    assert imported.time_us == 42


def test_decode_rejects_garbage() -> None:
    with pytest.raises(JetstreamDecodingError):
        decode_block(b'not a zstd frame')


def test_read_sealed_header_rejects_bad_magic() -> None:
    with pytest.raises(JetstreamDecodingError, match='magic'):
        read_sealed_header(b'nope' + bytes(252))


def test_read_sealed_header_rejects_active_segment() -> None:
    # an active segment leaves the header zeroed until seal
    with pytest.raises(JetstreamDecodingError, match='active'):
        read_sealed_header(b'jss0' + bytes(252))


def test_read_sealed_header_rejects_short_input() -> None:
    with pytest.raises(JetstreamDecodingError):
        read_sealed_header(b'jss0')


def test_matcher_selects_by_did(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(dids=['did:plc:aaa']).filter(events))

    assert matched
    assert {event.did for event in matched} == {'did:plc:aaa'}


def test_matcher_keeps_markers_under_a_collection_filter(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(collections=['app.bsky.feed.post']).filter(events))
    kinds = {event.kind for event in matched}

    # identity/account/sync are the only purge signals a folding consumer gets, so a
    # collection filter must not drop them
    assert {KIND_IDENTITY, KIND_ACCOUNT, KIND_SYNC} <= kinds
    assert all(event.collection == 'app.bsky.feed.post' for event in matched if event.is_commit)


def test_matcher_kinds_commit_drops_markers(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(kinds=['commit']).filter(events))

    assert matched
    assert all(event.is_commit for event in matched)


def test_matcher_kinds_selects_marker_kinds(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(kinds=['identity']).filter(events))

    assert [event.kind for event in matched] == [KIND_IDENTITY]


def test_matcher_collection_wildcard(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(kinds=['commit'], collections=['app.bsky.feed.*']).filter(events))

    assert matched
    assert all(event.collection.startswith('app.bsky.feed.') for event in matched)


def test_matcher_dids_apply_to_every_kind(events: t.List[SegmentEvent]) -> None:
    matched = list(RowMatcher(dids=['did:plc:cccccccccccc']).filter(events))

    assert [event.kind for event in matched] == [KIND_IDENTITY]


def test_matcher_seq_bounds_are_half_open(events: t.List[SegmentEvent]) -> None:
    after = list(RowMatcher(after_seq=13).filter(events))
    before = list(RowMatcher(before_seq=13).filter(events))

    assert [event.seq for event in after] == [14, 15, 16]  # exclusive lower bound
    assert [event.seq for event in before] == [10, 11, 12, 13]  # inclusive upper bound


def test_matcher_advance_to_raises_the_floor(events: t.List[SegmentEvent]) -> None:
    matcher = RowMatcher()

    matcher.advance_to(14)

    assert [event.seq for event in matcher.filter(events)] == [15, 16]


def test_matcher_advance_to_never_lowers_the_floor(events: t.List[SegmentEvent]) -> None:
    matcher = RowMatcher(after_seq=15)

    matcher.advance_to(11)

    assert [event.seq for event in matcher.filter(events)] == [16]
