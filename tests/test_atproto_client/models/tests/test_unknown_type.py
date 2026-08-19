"""Resolution of the ``UnknownType`` union.

``UnknownType`` is a left-to-right union so that a known record does not also get built as a
throwaway :obj:`DotDict`. These tests pin both halves of that: the fallback still happens for
everything the models cannot describe, and it no longer happens for everything they can.
"""

import typing as t

import pytest
from atproto_client import models
from atproto_client.models import dot_dict
from atproto_client.models.dot_dict import DotDict

#: CID of the DAG-CBOR block ``{'text': 'synthetic subject post'}``; no repo on the network holds it.
_SUBJECT_CID = 'bafyreidnwt5s2u353exextusedas4nr77z5rhgzmg5j2swdadb7n65wxsy'

_AUTHOR_DID = 'did:plc:aaaaaaaaaaaaaaaaaaaaaaaa'
_SUBJECT_DID = 'did:plc:bbbbbbbbbbbbbbbbbbbbbbbb'

_SUBJECT = {'cid': _SUBJECT_CID, 'uri': f'at://{_SUBJECT_DID}/app.bsky.feed.post/3aaaaaaaaaaac'}
_LIKE = {'$type': 'app.bsky.feed.like', 'createdAt': '2026-01-01T00:00:00Z', 'subject': _SUBJECT}

_COMMIT = {
    '$type': 'network.bsky.jetstream.subscribeEvents#commit',
    'collection': 'app.bsky.feed.like',
    'did': _AUTHOR_DID,
    'operation': 'create',
    'rev': '3aaaaaaaaaaaa',
    'rkey': '3aaaaaaaaaaab',
    'seq': 1,
    'time': '2026-01-01T00:00:00.000000Z',
}


def _parse_record(record: dict) -> t.Any:
    commit = models.NetworkBskyJetstreamSubscribeEvents.Commit.model_validate({**_COMMIT, 'record': record})
    return commit.record


def test_known_record_resolves_to_model() -> None:
    assert isinstance(_parse_record(_LIKE), models.AppBskyFeedLike.Record)


def test_extended_known_record_resolves_to_model() -> None:
    record = _parse_record({**_LIKE, 'via': None, 'custom': 'third-party client field'})

    assert isinstance(record, models.AppBskyFeedLike.Record)
    assert record['custom'] == 'third-party client field'


@pytest.mark.parametrize(
    'record',
    [
        pytest.param({'$type': 'com.example.thing', 'a': 1}, id='unknown_type'),
        pytest.param({'a': 1}, id='no_type'),
        pytest.param({'$type': 'com.example.thing', 'items': [{'a': 1}, {'b': 2}]}, id='nested_list'),
        pytest.param({'$type': 'app.bsky.feed.like', 'createdAt': '2026-01-01T00:00:00Z'}, id='missing_required'),
        pytest.param({'$type': 'app.bsky.feed.like', 'createdAt': 123, 'subject': _SUBJECT}, id='wrong_field_type'),
    ],
)
def test_undescribable_record_falls_back_to_dot_dict(record: dict) -> None:
    assert isinstance(_parse_record(record), DotDict)


def test_known_record_does_not_build_a_throwaway_dot_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    created = []
    original_init = DotDict.__init__

    def spy(self: DotDict, data: dict) -> None:
        created.append(data)
        original_init(self, data)

    monkeypatch.setattr(dot_dict.DotDict, '__init__', spy)

    assert isinstance(_parse_record(_LIKE), models.AppBskyFeedLike.Record)
    assert created == []
