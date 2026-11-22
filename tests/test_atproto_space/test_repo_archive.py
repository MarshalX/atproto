import typing as t

import pytest
from atproto_core.cbor import encode_dag
from atproto_core.cid import CID
from atproto_core.exceptions import InvalidStarError
from atproto_space.commit import verify_commit
from atproto_space.exceptions import SpaceRepoVerificationError
from atproto_space.models import RepoRecord
from atproto_space.repo_archive import REPO_ARCHIVE_TYPE, read_repo_archive, verify_repo_archive_records

from tests.test_atproto_space.star_builder import encode_repo_archive, encode_star

_REPO = 'did:web:author.example'
_SPACE = 'at://did:web:authority.example/space/com.example.space/skey'
_REV = '3mtwwsccuqy22'

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/verify_repo_test.go#L145-L162
_EMPTY_ARCHIVE = bytes.fromhex(
    '2a6c0100b701a6637265766d336d7477777363637571793232637665720164646174615820e5a00aa9991ac8a5ee3109844d84a55583'
    'bd20572ad3ffcd42792f3c36b183ad647265706f766469643a7765623a617574686f722e6578616d706c6565247479706572617470726f'
    '746f2d73706163652d7265706f657370616365783b61743a2f2f6469643a7765623a617574686f726974792e6578616d706c652f737061'
    '63652f636f6d2e6578616d706c652e73706163652f736b657900'
)
_EMPTY_DIGEST = bytes.fromhex('e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad')

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/verify_repo_test.go#L31-L45
_RECORD_PREFIX = bytes.fromhex('a265247479706572636f6d2e6578616d706c652e7265636f72646576616c7565')
_RECORDS = [
    ('com.example.record/aaaaaaaa', _RECORD_PREFIX + b'\x01'),
    ('com.example.record/b', _RECORD_PREFIX + b'\x02'),
    ('com.other.record/a', _RECORD_PREFIX + b'\x03'),
]
_CIDS = [
    'bafyreieie2lcmcbq7m7q5g5t2crp5sszk5uzs4kyh4v7nxth5zuudgexhi',
    'bafyreig3i7y3qv2wcrtatrwncps37yn23dvhbjvyzuimfgntgqnsyi4gqy',
    'bafyreia7nqjuedqpg3ityibxpj6wwfi6a3sctc2iwgia44rqeluxaeluee',
]
_LINK = encode_dag(CID.decode(_CIDS[0]))
# the test of indigo compares with a reference implementation, so the digest is computed
_DIGEST = bytes.fromhex('b1934b5f6c70bb67c202710a8c2d63e8d6b7029b468cff014babff34e8f1261c')

_Records = t.List[t.Tuple[str, bytes]]


def _build_commit(data: bytes = _DIGEST, **fields: t.Any) -> t.Dict[str, t.Any]:
    return {'ver': 1, 'repo': _REPO, 'space': _SPACE, 'rev': _REV, 'data': data, **fields}


def _verify(archive: bytes) -> t.List[RepoRecord]:
    star, commit = read_repo_archive(archive)
    return verify_repo_archive_records(star, commit)


def test_read_repo_archive() -> None:
    star, commit = read_repo_archive(_EMPTY_ARCHIVE)

    assert star.meta['$type'] == REPO_ARCHIVE_TYPE
    assert star.pairs == []
    assert commit.ver == 1
    assert commit.repo == _REPO
    assert commit.space == _SPACE
    assert commit.rev == _REV
    assert commit.data == _EMPTY_DIGEST


def test_empty_repo_archive_is_verified() -> None:
    star, commit = read_repo_archive(_EMPTY_ARCHIVE)

    verify_commit(commit, _SPACE, _REPO)

    assert verify_repo_archive_records(star, commit) == []


def test_star_builder_reproduces_empty_repo_archive() -> None:
    assert encode_repo_archive(_build_commit(_EMPTY_DIGEST)) == _EMPTY_ARCHIVE


def test_repo_archive_with_records_is_verified() -> None:
    star, commit = read_repo_archive(encode_repo_archive(_build_commit(), _RECORDS))

    verify_commit(commit, _SPACE, _REPO)
    records = verify_repo_archive_records(star, commit)

    assert commit.data == _DIGEST
    assert records == [
        RepoRecord('com.example.record', 'aaaaaaaa', _CIDS[0], {'$type': 'com.example.record', 'value': 1}),
        RepoRecord('com.example.record', 'b', _CIDS[1], {'$type': 'com.example.record', 'value': 2}),
        RepoRecord('com.other.record', 'a', _CIDS[2], {'$type': 'com.example.record', 'value': 3}),
    ]


@pytest.mark.parametrize(
    ('records', 'message'),
    [
        pytest.param(
            [_RECORDS[1], _RECORDS[0], _RECORDS[2]],
            'Records out of order at com.example.record/aaaaaaaa',
            id='out of order',
        ),
        pytest.param(
            [_RECORDS[0], _RECORDS[2], _RECORDS[1]], 'Records out of order at com.example.record/b', id='last first'
        ),
        pytest.param(
            [_RECORDS[0], *_RECORDS], 'Records out of order at com.example.record/aaaaaaaa', id='repeated path'
        ),
        pytest.param([('not-a-path', b'\xa0')], 'Invalid record path: not-a-path', id='path without a record key'),
        pytest.param(
            [('com.example.record/a/b', b'\xa0')], 'Invalid record path: com.example.record/a/b', id='path too long'
        ),
        pytest.param([('record/a', b'\xa0')], 'Invalid NSID in record path: record/a', id='path without an NSID'),
        pytest.param([('/a', b'\xa0')], 'Invalid NSID in record path: /a', id='path with an empty NSID'),
        pytest.param(
            [('com.example.record\n/a', b'\xa0')],
            'Invalid NSID in record path',
            id='path with a line break in the NSID',
        ),
        pytest.param(
            [('com.example.record/', b'\xa0')], 'Invalid record key in record path', id='path with an empty key'
        ),
        pytest.param([('com.example.record/..', b'\xa0')], 'Invalid record key in record path', id='path with dots'),
        pytest.param(
            [('com.example.record/a b', b'\xa0')], 'Invalid record key in record path', id='path with a space'
        ),
        pytest.param(
            [('com.example.record/a\n', b'\xa0')], 'Invalid record key in record path', id='path with a line break'
        ),
        pytest.param(
            [(f'com.example.record/{"a" * 513}', b'\xa0')], 'Invalid record key in record path', id='long record key'
        ),
        pytest.param([(_RECORDS[0][0], b'\xa1')], 'Invalid record at com.example.record/aaaaaaaa', id='not CBOR'),
        pytest.param(
            [(_RECORDS[0][0], encode_dag('hello'))], 'Invalid record at com.example.record/aaaaaaaa', id='not a map'
        ),
        pytest.param([(_RECORDS[0][0], encode_dag([1]))], 'Invalid record at com.example.record/aaaaaaaa', id='a list'),
        pytest.param(
            [(_RECORDS[0][0], _RECORD_PREFIX + b'\x18\x01')],
            'Invalid record at com.example.record/aaaaaaaa',
            id='integer not in the shortest form',
        ),
        pytest.param(
            [(_RECORDS[0][0], _RECORD_PREFIX + b'\xfa\x3f\xc0\x00\x00')],
            'Invalid record at com.example.record/aaaaaaaa',
            id='float of 32 bits',
        ),
        pytest.param(
            [(_RECORDS[0][0], _RECORD_PREFIX + b'\xd8\x2a\x58\x26' + _LINK[4:] + b'\x01')],
            'Invalid record at com.example.record/aaaaaaaa',
            id='link with a byte after the CID',
        ),
        pytest.param(_RECORDS[:-1], 'Records do not match the commit data', id='without a committed record'),
        pytest.param(
            [*_RECORDS, ('com.other.record/b', _RECORD_PREFIX + b'\x04')],
            'Records do not match the commit data',
            id='with an uncommitted record',
        ),
        pytest.param(
            [(_RECORDS[0][0], _RECORD_PREFIX + b'\x09'), *_RECORDS[1:]],
            'Records do not match the commit data',
            id='with another value',
        ),
        pytest.param(
            [('com.example.record/a', _RECORDS[0][1]), *_RECORDS[1:]],
            'Records do not match the commit data',
            id='with another path',
        ),
        pytest.param([], 'Records do not match the commit data', id='without records'),
    ],
)
def test_repo_archive_with_wrong_records_is_rejected(records: _Records, message: str) -> None:
    archive = encode_repo_archive(_build_commit(), records)

    with pytest.raises(SpaceRepoVerificationError, match=message):
        _verify(archive)


def test_repo_archive_with_path_that_is_not_utf8_is_rejected() -> None:
    archive = encode_star(encode_dag({'$type': REPO_ARCHIVE_TYPE, **_build_commit()}), [(b'\xff/a', b'\xa0')])

    with pytest.raises(SpaceRepoVerificationError, match='Invalid record path'):
        _verify(archive)


def test_records_are_verified_against_given_commit() -> None:
    star, commit = read_repo_archive(encode_repo_archive(_build_commit(), _RECORDS))

    with pytest.raises(SpaceRepoVerificationError, match='Records do not match the commit data'):
        verify_repo_archive_records(star, commit.model_copy(update={'data': _EMPTY_DIGEST}))


@pytest.mark.parametrize(
    ('meta', 'message'),
    [
        pytest.param({'$type': 'atproto-space-meta'}, 'Invalid repo metadata: expected type', id='another type'),
        pytest.param(
            {'$type': 'com.atproto.space.defs#commit'}, 'Invalid repo metadata: expected type', id='type of a commit'
        ),
        pytest.param({'ver': 2}, 'Unsupported commit version: 2', id='unknown version'),
        pytest.param({'ver': '1'}, 'Invalid repo metadata', id='version as a string'),
        pytest.param({'ver': True}, 'Invalid repo metadata', id='version as a boolean'),
        pytest.param({'rev': 1}, 'Invalid repo metadata', id='revision as an integer'),
        pytest.param({'repo': None}, 'Invalid repo metadata', id='repo as null'),
        pytest.param({'data': 'digest'}, 'Invalid repo metadata', id='data as a string'),
    ],
)
def test_repo_archive_with_wrong_metadata_is_rejected(meta: t.Dict[str, t.Any], message: str) -> None:
    archive = encode_repo_archive(_build_commit(**meta), _RECORDS)

    with pytest.raises(SpaceRepoVerificationError, match=message):
        read_repo_archive(archive)


@pytest.mark.parametrize('field', ['ver', 'repo', 'space', 'rev', 'data'])
def test_repo_archive_without_commit_field_is_rejected(field: str) -> None:
    commit = _build_commit()
    del commit[field]

    with pytest.raises(SpaceRepoVerificationError, match='Invalid repo metadata'):
        read_repo_archive(encode_repo_archive(commit, _RECORDS))


def test_repo_archive_keeps_malformed_commit_for_verification() -> None:
    _, commit = read_repo_archive(encode_repo_archive(_build_commit(bytes(31), rev='not-a-tid')))

    with pytest.raises(SpaceRepoVerificationError, match='Commit revision is not a TID'):
        verify_commit(commit, _SPACE, _REPO)


@pytest.mark.parametrize(
    ('commit', 'records', 'limit'),
    [
        pytest.param(_build_commit(filler='x' * 64 * 1024), [], 64 * 1024, id='metadata'),
        pytest.param(_build_commit(), [(f'com.example.record/{"x" * 4 * 1024}', b'\xa0')], 4 * 1024, id='path'),
        pytest.param(_build_commit(), [(_RECORDS[0][0], bytes(1024 * 1024 + 1))], 1024 * 1024, id='record'),
    ],
)
def test_repo_archive_over_limit_is_rejected(commit: t.Dict[str, t.Any], records: _Records, limit: int) -> None:
    with pytest.raises(InvalidStarError, match=f'exceeds limit of {limit}'):
        read_repo_archive(encode_repo_archive(commit, records))


def test_repo_archive_accepts_record_at_limit() -> None:
    record = encode_dag({'text': 'x' * (1024 * 1024 - 11)})
    archive = encode_repo_archive(_build_commit(), [(_RECORDS[0][0], record)])

    star, _ = read_repo_archive(archive)

    assert len(record) == 1024 * 1024
    assert star.pairs == [(_RECORDS[0][0].encode(), record)]


@pytest.mark.parametrize('archive', [b'', _EMPTY_ARCHIVE[:-1], _EMPTY_ARCHIVE + b'\x00', b'\x00' + _EMPTY_ARCHIVE])
def test_malformed_repo_archive_is_rejected(archive: bytes) -> None:
    with pytest.raises(InvalidStarError):
        read_repo_archive(archive)
