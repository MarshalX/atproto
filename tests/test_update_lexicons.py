import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from update_lexicons import (
    _SOURCES,
    LexiconSource,
    SourceRevision,
    _build_body,
    _build_commit_message,
    _build_title,
    _diff_lexicons,
    _format_lexicon_filename,
    _merge_extracted_lexicons,
    _set_output,
    _short_path,
)

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


def _lexicon(defs: dict) -> dict:
    return {'lexicon': 1, 'defs': defs}


def _query(**properties: dict) -> dict:
    return _lexicon({'main': {'type': 'query', 'parameters': {'type': 'params', 'properties': properties}}})


def test_description_churn_is_not_a_semantic_change() -> None:
    old = {'app.bsky.feed.getPosts': _lexicon({'main': {'type': 'query', 'description': 'Old wording.'}})}
    new = {'app.bsky.feed.getPosts': _lexicon({'main': {'type': 'query', 'description': 'New wording.'}})}

    diff = _diff_lexicons(old, new)

    assert diff.description_only == ['app.bsky.feed.getPosts']
    assert diff.changed_lexicons == []
    assert _build_title(diff) == 'Update lexicons: descriptions only (1 lexicon)'


def test_a_new_field_is_reported_once_not_per_leaf() -> None:
    old = _query(cursor={'type': 'string'})
    new = _query(
        cursor={'type': 'string'}, languages={'type': 'array', 'items': {'type': 'string', 'format': 'language'}}
    )

    diff = _diff_lexicons({'app.bsky.feed.searchPosts': old}, {'app.bsky.feed.searchPosts': new})

    assert diff.added_fields == ['app.bsky.feed.searchPosts#main.parameters.properties.languages']
    assert diff.constraints == []


def test_dropping_a_constraint_does_not_read_as_dropping_the_field() -> None:
    old = _query(tags={'type': 'array', 'maxLength': 8})
    new = _query(tags={'type': 'array'})

    diff = _diff_lexicons({'app.bsky.feed.searchPosts': old}, {'app.bsky.feed.searchPosts': new})

    assert diff.removed_fields == []
    assert [change.path for change in diff.constraints] == [
        'app.bsky.feed.searchPosts#main.parameters.properties.tags.maxLength'
    ]


def test_a_renamed_field_is_both_an_addition_and_a_removal() -> None:
    old = _query(language={'type': 'string'})
    new = _query(languages={'type': 'array', 'items': {'type': 'string'}})

    diff = _diff_lexicons({'app.bsky.feed.searchPostsV2': old}, {'app.bsky.feed.searchPostsV2': new})

    assert [_short_path(field) for field in diff.added_fields] == ['app.bsky.feed.searchPostsV2.languages']
    assert [_short_path(field) for field in diff.removed_fields] == ['app.bsky.feed.searchPostsV2.language']


def test_permission_set_churn_is_bucketed_away_from_real_changes() -> None:
    old = {'app.bsky.authFullApp': _lexicon({'main': {'type': 'permission-set', 'permissions': ['a']}})}
    new = {'app.bsky.authFullApp': _lexicon({'main': {'type': 'permission-set', 'permissions': ['a', 'b']}})}

    diff = _diff_lexicons(old, new)

    assert diff.permission_sets == ['app.bsky.authFullApp']
    assert diff.constraints == []


def test_title_names_the_added_lexicon() -> None:
    diff = _diff_lexicons({}, {'app.bsky.graph.searchStarterPacksV2': _lexicon({'main': {'type': 'query'}})})

    assert _build_title(diff) == 'Update lexicons: add app.bsky.graph.searchStarterPacksV2'


def test_title_groups_siblings_and_prefers_the_most_visible_namespace() -> None:
    added = ['app.bsky.embed.gallery', 'chat.bsky.moderation.getConvo', 'chat.bsky.moderation.getConvos']
    diff = _diff_lexicons({}, {nsid: _lexicon({'main': {'type': 'query'}}) for nsid in added})

    # chat.bsky.moderation.* is the bigger group, but app.bsky is what SDK users notice first
    assert _build_title(diff) == 'Update lexicons: add app.bsky.embed.gallery, chat.bsky.moderation.*'


def test_title_stays_within_the_length_budget() -> None:
    added = [f'app.bsky.unspecced.someVeryLongProcedureName{index}' for index in range(20)]
    diff = _diff_lexicons({}, {nsid: _lexicon({'main': {'type': 'query'}}) for nsid in added})

    assert len(_build_title(diff)) <= 72


def test_title_falls_back_to_a_count_when_nothing_was_added() -> None:
    old = _query(tags={'type': 'array', 'maxLength': 8})
    new = _query(tags={'type': 'array', 'maxLength': 4})

    diff = _diff_lexicons({'app.bsky.feed.searchPosts': old}, {'app.bsky.feed.searchPosts': new})

    assert _build_title(diff) == 'Update lexicons (1 changed)'


def test_short_path_reads_as_the_api_surface() -> None:
    path = 'tools.ozone.queue.createQueue#main.input.schema.properties.subjectTypes.items.knownValues'

    assert _short_path(path) == 'tools.ozone.queue.createQueue.input.subjectTypes[].knownValues'


def test_commit_message_carries_a_trailer_per_source() -> None:
    revisions = [
        SourceRevision(_ATPROTO, 'c400731' + '0' * 33, '2026-08-20T13:33:59Z'),
        SourceRevision(_JETSTREAM, '11e399d' + '0' * 33, '2026-08-12T16:51:26Z'),
    ]

    message = _build_commit_message('Update lexicons: add app.bsky.embed.gallery', revisions)

    subject, blank, *trailers = message.split('\n')
    assert subject == 'Update lexicons: add app.bsky.embed.gallery'
    assert blank == ''
    assert trailers == [
        f'Lexicon-Source: bluesky-social/atproto@{revisions[0].sha} 2026-08-20T13:33:59Z',
        f'Lexicon-Source: bluesky-social/jetstream@{revisions[1].sha} 2026-08-12T16:51:26Z',
    ]


def test_body_links_every_source_commit() -> None:
    revisions = [SourceRevision(_ATPROTO, 'c400731' + '0' * 33, '2026-08-20T13:33:59Z')]
    diff = _diff_lexicons({}, {'app.bsky.embed.gallery': _lexicon({'main': {'type': 'object'}})})

    body = _build_body(diff, revisions)

    assert f'https://github.com/bluesky-social/atproto/commit/{revisions[0].sha}' in body
    assert '- `app.bsky.embed.gallery`' in body


def test_multiline_output_is_written_with_a_heredoc_delimiter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output = tmp_path / 'github_output'
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))

    _set_output('body', 'first line\nsecond line')

    written = output.read_text(encoding='UTF-8')
    header, *rest = written.splitlines()
    name, _, delimiter = header.partition('<<')
    assert name == 'body'
    assert rest == ['first line', 'second line', delimiter]


def test_ozone_never_headlines_a_title_that_has_anything_else() -> None:
    added = ['tools.ozone.report.closeReports', 'tools.ozone.queue.listQueues', 'app.bsky.embed.gallery']
    diff = _diff_lexicons({}, {nsid: _lexicon({'main': {'type': 'query'}}) for nsid in added})

    assert _build_title(diff) == 'Update lexicons: add app.bsky.embed.gallery'


def test_ozone_churn_does_not_inflate_the_changed_count() -> None:
    old = {
        'app.bsky.feed.searchPosts': _query(tags={'type': 'array', 'maxLength': 8}),
        'tools.ozone.queue.defs': _query(subjectTypes={'type': 'array', 'maxLength': 8}),
        'internal.bsky.actor.getProfiles': _query(actors={'type': 'array', 'maxLength': 8}),
    }
    new = {
        'app.bsky.feed.searchPosts': _query(tags={'type': 'array', 'maxLength': 4}),
        'tools.ozone.queue.defs': _query(subjectTypes={'type': 'array', 'maxLength': 4}),
        'internal.bsky.actor.getProfiles': _query(actors={'type': 'array', 'maxLength': 4}),
    }

    diff = _diff_lexicons(old, new)

    assert len(diff.changed_lexicons) == 3
    assert _build_title(diff) == 'Update lexicons (1 changed)'


def test_an_ozone_only_update_still_gets_a_meaningful_title() -> None:
    diff = _diff_lexicons({}, {'tools.ozone.report.closeReports': _lexicon({'main': {'type': 'procedure'}})})

    assert _build_title(diff) == 'Update lexicons: add tools.ozone.report.closeReports'


def test_body_folds_ozone_changes_into_a_collapsed_block() -> None:
    revisions = [SourceRevision(_ATPROTO, 'c400731' + '0' * 33, '2026-08-20T13:33:59Z')]
    added = ['app.bsky.embed.gallery', 'tools.ozone.report.closeReports']
    diff = _diff_lexicons({}, {nsid: _lexicon({'main': {'type': 'query'}}) for nsid in added})

    body = _build_body(diff, revisions)
    headline, _, folded = body.partition('<details>')

    assert '- `app.bsky.embed.gallery`' in headline
    assert 'tools.ozone' not in headline
    assert '- `tools.ozone.report.closeReports`' in folded


def test_jetstream_namespace_is_primary_and_outranks_chat_churn() -> None:
    added = ['network.bsky.jetstream.subscribeEvents', 'chat.bsky.group.editGroup', 'site.standard.document']
    diff = _diff_lexicons({}, {nsid: _lexicon({'main': {'type': 'query'}}) for nsid in added})

    # jetstream ships as its own package and is fetched from its own source repo
    assert _build_title(diff).startswith('Update lexicons: add network.bsky.jetstream.subscribeEvents')


def test_jetstream_changes_are_never_folded_away() -> None:
    revisions = [SourceRevision(_JETSTREAM, '11e399d' + '0' * 33, '2026-08-12T16:51:26Z')]
    diff = _diff_lexicons({}, {'network.bsky.jetstream.subscribeEvents': _lexicon({'main': {'type': 'subscription'}})})

    headline, _, folded = _build_body(diff, revisions).partition('<details>')

    assert '- `network.bsky.jetstream.subscribeEvents`' in headline
    assert folded == ''
