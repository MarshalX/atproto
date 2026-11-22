import stat
import sys
import typing as t
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from update_lexicons import (
    _SOURCES,
    _SPACES_COMMIT,
    LexiconSource,
    SourceRevision,
    _build_body,
    _build_commit_message,
    _build_last_commit_api_params,
    _build_src_download_url,
    _build_title,
    _diff_lexicons,
    _extract_zip,
    _format_lexicon_filename,
    _merge_extracted_lexicons,
    _set_output,
    _short_path,
)

_ATPROTO = LexiconSource(repo='atproto')
_ATPROTO_BSKY = LexiconSource(repo='atproto', lexicons_dir='packages/bsky/lexicons')
_JETSTREAM = LexiconSource(repo='jetstream', subpaths=('network/',))
_PINNED = LexiconSource(
    repo='atproto',
    branch='permissioned-data',
    commit='b5fd12f' + '0' * 33,
    subpaths=('com/atproto/space/', 'com/atproto/memberspace/'),
)


def test_jetstream_source_is_restricted_to_its_own_namespace() -> None:
    jetstream = next(source for source in _SOURCES if source.repo == 'jetstream')

    assert jetstream.subpaths == ('network/',)


def test_spaces_lexicons_come_from_the_only_pinned_source() -> None:
    pinned = [source for source in _SOURCES if source.commit]

    assert [source.commit for source in pinned] == [_SPACES_COMMIT]
    assert pinned[0].subpaths == (
        'com/atproto/space/',
        'com/atproto/memberspace/',
        'com/atproto/managedspace/',
        'com/atproto/personalspace/',
    )


def test_source_is_downloaded_from_the_branch_head_unless_pinned() -> None:
    assert _build_src_download_url(_ATPROTO) == 'https://github.com/bluesky-social/atproto/archive/refs/heads/main.zip'
    assert _build_src_download_url(_PINNED) == f'https://github.com/bluesky-social/atproto/archive/{_PINNED.commit}.zip'


def test_last_commit_is_looked_up_under_the_lexicons_of_the_source() -> None:
    assert _build_last_commit_api_params(_ATPROTO) == {'sha': 'main', 'per_page': 1, 'path': 'lexicons'}
    assert _build_last_commit_api_params(_ATPROTO_BSKY)['path'] == 'packages/bsky/lexicons'
    assert _build_last_commit_api_params(_JETSTREAM)['path'] == 'lexicons/network'


def test_last_commit_of_a_pinned_source_is_the_pin_itself() -> None:
    assert _build_last_commit_api_params(_PINNED) == {'sha': _PINNED.commit, 'per_page': 1}


def test_nsid_path_is_flattened_into_the_filename() -> None:
    path = 'jetstream-main/lexicons/network/bsky/jetstream/subscribeEvents.json'

    filename = _format_lexicon_filename(path, _JETSTREAM)

    assert filename == 'network.bsky.jetstream.subscribeEvents.json'


def _zip(files: t.Dict[str, bytes], symlinks: t.Dict[str, str]) -> BytesIO:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
        for name, target in symlinks.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, target)

    return buffer


def test_package_snapshot_lexicons_are_extracted_with_symlinks_resolved() -> None:
    override = 'lexicons-overrides/app/bsky/embed/external.json'
    archive = _zip(
        {
            'atproto-main/lexicons/com/atproto/repo/strongRef.json': b'{"id": "com.atproto.repo.strongRef"}',
            'atproto-main/lexicons-overrides/app/bsky/embed/external.json': b'{"id": "app.bsky.embed.external"}',
            'atproto-main/packages/bsky/lexicons/app/bsky/actor/defs.json': b'{"id": "app.bsky.actor.defs"}',
            'atproto-main/packages/bsky/lexicons/README.md': b'# readme',
        },
        {'atproto-main/packages/bsky/lexicons/app/bsky/embed/external.json': f'{"../" * 6}{override}'},
    )

    assert _extract_zip(archive, _ATPROTO_BSKY) == {
        'app.bsky.actor.defs.json': b'{"id": "app.bsky.actor.defs"}',
        'app.bsky.embed.external.json': b'{"id": "app.bsky.embed.external"}',
    }


def test_pinned_source_lexicons_are_extracted_from_every_subtree_of_the_commit_archive() -> None:
    root = f'atproto-{_PINNED.commit}/lexicons/com/atproto'
    archive = _zip(
        {
            f'{root}/space/getRecord.json': b'{"id": "com.atproto.space.getRecord"}',
            f'{root}/memberspace/listMembers.json': b'{"id": "com.atproto.memberspace.listMembers"}',
            f'{root}/spaces/getRecord.json': b'{"id": "com.atproto.spaces.getRecord"}',
            f'{root}/repo/getRecord.json': b'{"id": "com.atproto.repo.getRecord"}',
            'atproto-permissioned-data/lexicons/com/atproto/space/putRecord.json': b'{}',
        },
        {},
    )

    assert _extract_zip(archive, _PINNED) == {
        'com.atproto.space.getRecord.json': b'{"id": "com.atproto.space.getRecord"}',
        'com.atproto.memberspace.listMembers.json': b'{"id": "com.atproto.memberspace.listMembers"}',
    }


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


@pytest.mark.parametrize('pinned_first', [True, False])
def test_merge_prefers_an_unpinned_source_over_a_pinned_one(
    pinned_first: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv('CI', raising=False)
    pinned = (
        _PINNED,
        {
            'com.atproto.space.getRecord.json': b'{"pinned": true}',
            'com.atproto.space.putRecord.json': b'{"pinned": true}',
            'com.atproto.space.listSpaces.json': b'{"pinned": true}',
        },
    )
    unpinned = (
        _ATPROTO,
        {'com.atproto.space.getRecord.json': b'{}', 'com.atproto.space.putRecord.json': b'{}'},
    )

    merged = _merge_extracted_lexicons([pinned, unpinned] if pinned_first else [unpinned, pinned])

    assert merged == {
        'com.atproto.space.getRecord.json': b'{}',
        'com.atproto.space.putRecord.json': b'{}',
        'com.atproto.space.listSpaces.json': b'{"pinned": true}',
    }
    assert capsys.readouterr().out.splitlines() == [
        '- Dropped 2 lexicons of the pinned atproto@b5fd12f, now provided by atproto; remove the pin'
    ]


def test_merge_is_silent_while_the_pinned_lexicons_are_not_upstream(capsys: pytest.CaptureFixture[str]) -> None:
    merged = _merge_extracted_lexicons(
        [
            (_ATPROTO, {'com.atproto.repo.getRecord.json': b'{}'}),
            (_PINNED, {'com.atproto.space.getRecord.json': b'{}'}),
        ]
    )

    assert sorted(merged) == ['com.atproto.repo.getRecord.json', 'com.atproto.space.getRecord.json']
    assert capsys.readouterr() == ('', '')


def test_merge_rejects_a_lexicon_claimed_by_two_pinned_sources() -> None:
    duplicated = {'com.atproto.space.getRecord.json': b'{}'}

    with pytest.raises(RuntimeError, match='provided by both'):
        _merge_extracted_lexicons([(_PINNED, duplicated), (_PINNED._replace(commit='9bd8007' + '0' * 33), duplicated)])


def _lexicon(defs: t.Dict[str, object]) -> t.Dict[str, object]:
    return {'lexicon': 1, 'defs': defs}


def _query(**properties: t.Dict[str, object]) -> t.Dict[str, object]:
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


def test_commit_message_carries_one_trailer_for_the_pinned_source() -> None:
    revisions = [
        SourceRevision(source, source.commit or 'c400731' + '0' * 33, '2026-08-20T13:33:59Z') for source in _SOURCES
    ]

    message = _build_commit_message('Update lexicons', revisions)

    assert message.count(f'Lexicon-Source: bluesky-social/atproto@{_SPACES_COMMIT} ') == 1
    assert message.count('Lexicon-Source: ') == len(_SOURCES)


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
