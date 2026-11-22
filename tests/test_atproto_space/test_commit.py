import typing as t

import pytest
from atproto_client import models
from atproto_crypto.lthash import LTHASH_STATE_SIZE, LtHash
from atproto_space.commit import COMMIT_VERSION, RepoCommit, verify_commit
from atproto_space.exceptions import SpaceRepoVerificationError
from atproto_space.models import RepoRecord

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/repo-commit.test.ts
_CID_A = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
_CID_B = 'bafyreidpw4cbv6gr4ukh33z23pvvrpr3wi4gnpmi4doamlsl3sa4rgri2a'

_SPACE = 'at://did:example:space/space/app.bsky.group/test'
_REPO = 'did:example:alice'
# the revision of the upstream tests, 3kbcq3p7ad400, is not a TID
_REV = '3mtwwsccuqy22'

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/verify_repo_test.go#L31-L45
_INDIGO_RECORDS = [
    RepoRecord('com.example.record', 'aaaaaaaa', 'bafyreieie2lcmcbq7m7q5g5t2crp5sszk5uzs4kyh4v7nxth5zuudgexhi', {}),
    RepoRecord('com.example.record', 'b', 'bafyreig3i7y3qv2wcrtatrwncps37yn23dvhbjvyzuimfgntgqnsyi4gqy', {}),
    RepoRecord('com.other.record', 'a', 'bafyreia7nqjuedqpg3ityibxpj6wwfi6a3sctc2iwgia44rqeluxaeluee', {}),
]
# the test of indigo compares with a reference implementation, so the digest is computed
_INDIGO_DIGEST = bytes.fromhex('b1934b5f6c70bb67c202710a8c2d63e8d6b7029b468cff014babff34e8f1261c')

_EMPTY_DIGEST = bytes.fromhex('e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad')


def _build_commit(repo_commit: RepoCommit, **fields: t.Any) -> models.ComAtprotoSpaceDefs.Commit:
    commit = models.ComAtprotoSpaceDefs.Commit(
        ver=COMMIT_VERSION, space=_SPACE, repo=_REPO, rev=_REV, data=LtHash(repo_commit.state).digest()
    )

    return commit.model_copy(update=fields)


def _build_repo_commit(*records: t.Tuple[str, str, str]) -> RepoCommit:
    repo_commit = RepoCommit()
    for collection, rkey, cid in records:
        repo_commit.add(collection, rkey, cid)

    return repo_commit


def test_repo_commit_hashes_each_record_as_collection_rkey_cid_element() -> None:
    repo_commit = _build_repo_commit(('app.bsky.feed.post', '1', _CID_A), ('app.bsky.feed.like', '2', _CID_B))

    expected = LtHash()
    expected.add(f'app.bsky.feed.post/1/{_CID_A}')
    expected.add(f'app.bsky.feed.like/2/{_CID_B}')

    assert repo_commit.state == expected.state


def test_repo_commit_of_empty_repo() -> None:
    repo_commit = RepoCommit()

    assert repo_commit.state == bytes(LTHASH_STATE_SIZE)
    assert repo_commit.matches(_build_commit(repo_commit, data=_EMPTY_DIGEST))


def test_repo_commit_distinguishes_same_cid_at_different_paths() -> None:
    assert _build_repo_commit(('n.c.a', '1', _CID_A)).state != _build_repo_commit(('n.c.a', '2', _CID_A)).state


def test_repo_commit_distinguishes_different_cids_at_same_path() -> None:
    assert _build_repo_commit(('n.c.a', '1', _CID_A)).state != _build_repo_commit(('n.c.a', '1', _CID_B)).state


def test_repo_commit_from_records() -> None:
    repo_commit = RepoCommit.from_records(_INDIGO_RECORDS)

    incremental = _build_repo_commit(*((record.collection, record.rkey, record.cid) for record in _INDIGO_RECORDS))

    assert repo_commit.state == incremental.state
    assert repo_commit.matches(_build_commit(repo_commit, data=_INDIGO_DIGEST))


def test_repo_commit_does_not_depend_on_order_of_records() -> None:
    repo_commit = RepoCommit.from_records(reversed(_INDIGO_RECORDS))

    assert repo_commit.matches(_build_commit(repo_commit, data=_INDIGO_DIGEST))


def test_repo_commit_continues_from_state() -> None:
    repo_commit = _build_repo_commit(('n.c.a', '1', _CID_A))

    continued = RepoCommit(repo_commit.state)
    continued.add('n.c.b', '2', _CID_B)

    assert RepoCommit(repo_commit.state).state == repo_commit.state
    assert continued.state == _build_repo_commit(('n.c.a', '1', _CID_A), ('n.c.b', '2', _CID_B)).state


def test_repo_commit_rejects_state_of_another_size() -> None:
    with pytest.raises(ValueError, match='LtHash state must be 2048 bytes'):
        RepoCommit(bytes(32))


def test_repo_commit_removes_record() -> None:
    repo_commit = _build_repo_commit(('n.c.a', '1', _CID_A), ('n.c.b', '2', _CID_B))

    repo_commit.remove('n.c.b', '2', _CID_B)

    assert repo_commit.state == _build_repo_commit(('n.c.a', '1', _CID_A)).state


def test_repo_commit_applies_create() -> None:
    repo_commit = RepoCommit()

    repo_commit.apply('n.c.a', '1', _CID_A, None)

    assert repo_commit.state == _build_repo_commit(('n.c.a', '1', _CID_A)).state


def test_repo_commit_applies_delete() -> None:
    repo_commit = _build_repo_commit(('n.c.a', '1', _CID_A))

    repo_commit.apply('n.c.a', '1', None, _CID_A)

    assert repo_commit.state == RepoCommit().state


def test_repo_commit_applies_update() -> None:
    repo_commit = _build_repo_commit(('n.c.a', '1', _CID_A))

    repo_commit.apply('n.c.a', '1', _CID_B, _CID_A)

    assert repo_commit.state == _build_repo_commit(('n.c.a', '1', _CID_B)).state


def test_repo_commit_matches_only_commit_of_its_records() -> None:
    repo_commit = _build_repo_commit(('n.c.a', '1', _CID_A))
    commit = _build_commit(repo_commit)

    assert repo_commit.matches(commit)

    repo_commit.add('n.c.a', '2', _CID_B)

    assert not repo_commit.matches(commit)


def test_verify_commit() -> None:
    verify_commit(_build_commit(RepoCommit()), _SPACE, _REPO)


@pytest.mark.parametrize(
    ('fields', 'message'),
    [
        ({'ver': 2}, 'Unsupported commit version: 2'),
        ({'ver': 0}, 'Unsupported commit version: 0'),
        ({'repo': 'did:example:bob'}, 'Commit is for another repo: did:example:bob'),
        ({'space': 'at://did:example:space/space/app.bsky.group/other'}, 'Commit is for another space'),
        ({'rev': 'not-a-tid'}, 'Commit revision is not a TID'),
        ({'rev': '3kbcq3p7ad400'}, 'Commit revision is not a TID'),
        ({'rev': _REV[:-1]}, 'Commit revision is not a TID'),
        ({'rev': f'{_REV}\n'}, 'Commit revision is not a TID'),
        ({'data': bytes(31)}, 'Commit data must be 32 bytes, got 31'),
        ({'data': bytes(33)}, 'Commit data must be 32 bytes, got 33'),
        ({'data': b''}, 'Commit data must be 32 bytes, got 0'),
    ],
)
def test_verify_commit_rejects_commit(fields: t.Dict[str, t.Any], message: str) -> None:
    with pytest.raises(SpaceRepoVerificationError, match=message):
        verify_commit(_build_commit(RepoCommit(), **fields), _SPACE, _REPO)


@pytest.mark.parametrize(
    ('space', 'repo', 'message'),
    [
        ('at://did:example:space/space/app.bsky.group/other', _REPO, 'Commit is for another space'),
        (_SPACE, 'did:example:bob', 'Commit is for another repo'),
    ],
)
def test_verify_commit_rejects_commit_of_another_request(space: str, repo: str, message: str) -> None:
    with pytest.raises(SpaceRepoVerificationError, match=message):
        verify_commit(_build_commit(RepoCommit()), space, repo)
