import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from update_lexicons import _SOURCES, LexiconSource, _format_lexicon_filename, _merge_extracted_lexicons

_ATPROTO = LexiconSource(repo='atproto')
_JETSTREAM = LexiconSource(repo='jetstream', subpath='network/')


def test_jetstream_source_is_restricted_to_its_own_namespace() -> None:
    jetstream = next(source for source in _SOURCES if source.repo == 'jetstream')

    assert jetstream.subpath == 'network/'


def test_nsid_path_is_flattened_into_the_filename() -> None:
    path = 'jetstream-main/lexicons/network/bsky/jetstream/subscribeEvents.json'

    filename = _format_lexicon_filename(path, _JETSTREAM)

    assert filename == 'network.bsky.jetstream.subscribeEvents.json'


def test_merge_keeps_lexicons_of_every_source() -> None:
    merged = _merge_extracted_lexicons(
        [
            (_ATPROTO, {'com.atproto.sync.subscribeRepos.json': b'{}'}),
            (_JETSTREAM, {'network.bsky.jetstream.subscribeEvents.json': b'{}'}),
        ]
    )

    assert sorted(merged) == ['com.atproto.sync.subscribeRepos.json', 'network.bsky.jetstream.subscribeEvents.json']


def test_merge_rejects_a_lexicon_claimed_by_two_sources() -> None:
    # the jetstream repo vendors its own copy of subscribeRepos; taking both would be silent divergence
    duplicated = {'com.atproto.sync.subscribeRepos.json': b'{}'}

    with pytest.raises(RuntimeError, match='provided by both'):
        _merge_extracted_lexicons([(_ATPROTO, duplicated), (_JETSTREAM, duplicated)])
