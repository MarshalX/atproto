import hashlib
import typing as t

import httpx
import pytest
from atproto_client import models
from atproto_client.exceptions import BadRequestError, ModelError, RequestException
from atproto_client.models.dot_dict import DotDict
from atproto_client.request import Request
from atproto_core.cid import CID
from atproto_core.exceptions import InvalidStarError
from atproto_crypto.lthash import LTHASH_STATE_SIZE
from atproto_space import RecordChange, RepoChanges, RepoHead, RepoRecord, RepoSnapshot, SpaceReader, SpaceType
from atproto_space._data import encode_json_value, get_record_cid
from atproto_space.commit import RepoCommit
from atproto_space.exceptions import RepoGapError, SpaceIdentityError, SpaceMacError, SpaceRepoVerificationError
from atproto_space.reader import CidLookup

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    ALICE_PDS,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    FakeIdResolver,
    FakeSpaceNetwork,
    Record,
    Repo,
    build_network,
    delegation_token_provider,
    parse_mac_request,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_LIST_WRITERS = 'com.atproto.space.listWriters'
_GET_RECORD = 'com.atproto.space.getRecord'
_GET_REPO = 'com.atproto.space.getRepo'
_LIST_REPO_OPS = 'com.atproto.space.listRepoOps'

_REPO_WRITE = 'com.atproto.space.defs#repoWrite'

_NOTE = 'com.example.note'
_POST = 'app.bsky.feed.post'
_OTHER = 'com.example.other'
_GROUP = SpaceType('com.example.group', 'any', (_NOTE, _POST))

# DAG-CBOR of a note that holds 500 maps, one in another
_DEEP_NOTE = b'\xa2\x61a' + b'\xa1\x61a' * 500 + b'\x01\x65$type\x70' + _NOTE.encode()

_OLD_REV = '3jzfcijpj2z2a'
_LATE_CURSOR = '7zzzzzzzzzzzz/0'
_MAX_PAGES = 5
# CID of the record {'text': 'hello'}
_OTHER_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
# CID of the raw bytes b'hello'
_OTHER_BLOB_CID = 'bafkreibm6jg3ux5qumhcn2b3flc3tyu6dmlb4xa7u5bf44yegnrjhc4yeq'
# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/lthash.test.ts
_EMPTY_DIGEST = bytes.fromhex('e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad')

_Page = t.Dict[str, t.Any]
_Pairs = t.List[t.Tuple[str, bytes]]
_Read = t.Callable[[SpaceReader], object]


def make_reader(network: FakeSpaceNetwork, space_type: t.Optional[SpaceType] = None, **kwargs: t.Any) -> SpaceReader:
    kwargs.setdefault('delegation_token_provider', delegation_token_provider(network, ALICE_DID))
    kwargs.setdefault('id_resolver', FakeIdResolver(network))
    kwargs.setdefault('request', Request(transport=network.transport))

    return SpaceReader(SPACE, space_type, **kwargs)


def _note(text: str) -> t.Dict[str, t.Any]:
    return {'$type': _NOTE, 'text': text}


def _put_note(network: FakeSpaceNetwork, repo: str, rkey: str, text: str = 'hello') -> str:
    return network.put_record(SPACE, repo, _NOTE, rkey, _note(text))


@pytest.fixture
def network() -> FakeSpaceNetwork:
    network = build_network()
    _put_note(network, BOB_DID, 'kept', 'kept')
    _put_note(network, BOB_DID, 'updated', 'before')

    return network


def _lookup(snapshot: RepoSnapshot) -> CidLookup:
    index = {(record.collection, record.rkey): record.cid for record in snapshot.records}

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        return index.get((collection, rkey))

    return lookup


def _no_records(_: str, __: str) -> t.Optional[str]:
    return None


def _get_repo(reader: SpaceReader) -> object:
    return reader.get_repo(BOB_DID)


def _list_repo_ops(reader: SpaceReader) -> object:
    return reader.list_repo_ops(BOB_DID)


# the reads of this module that are verified against a MAC
_MAC_READS = [
    pytest.param(_GET_REPO, _get_repo, 'failed verification', id='repo'),
    pytest.param(_LIST_REPO_OPS, _list_repo_ops, 'commit failed verification', id='ops'),
]


def _key_shares(network: FakeSpaceNetwork, nsid: str) -> t.List[str]:
    key_shares: t.List[str] = []
    for request in network.requests_to(nsid):
        mac_request = parse_mac_request(request.headers['accept-signature'], 'atproto-space-commit')
        assert mac_request is not None
        key_shares.append(mac_request.key_share)

    return key_shares


def _edit_op(index: int, **changes: t.Any) -> t.Callable[[_Page], None]:
    def edit(page: _Page) -> None:
        page['ops'][index].update(changes)

    return edit


def _drop_values(page: _Page) -> None:
    for op in page['ops']:
        op.pop('value', None)


def _write_after_the_snapshot(network: FakeSpaceNetwork) -> None:
    """Write to the repo the way the test of upstream does: an update, a creation, and a record that does not last."""
    _put_note(network, BOB_DID, 'updated', 'after')
    _put_note(network, BOB_DID, 'created', 'created')
    _put_note(network, BOB_DID, 'transient', 'transient')
    network.delete_record(SPACE, BOB_DID, _NOTE, 'transient')


def test_get_repo_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    resolver = FakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    snapshot = reader.get_repo(BOB_DID)

    request = network.requests_to(_GET_REPO)[0]
    key_share = _key_shares(network, _GET_REPO)[0]
    records = network.repos[(SPACE, BOB_DID)].records
    assert isinstance(snapshot, RepoSnapshot)
    assert snapshot.commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert snapshot.records == [
        RepoRecord(_NOTE, 'kept', records[f'{_NOTE}/kept'].cid, _note('kept')),
        RepoRecord(_NOTE, 'updated', records[f'{_NOTE}/updated'].cid, _note('before')),
    ]
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200), (BOB_PDS, _GET_REPO, 200)]
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert request.headers['accept-signature'] == (
        f'mac=("atproto-space-commit";sf);keyid="{key_share}";tag="atproto-space-commit"'
    )
    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, False), (AUTHORITY_DID, False)]


def test_snapshot_holds_the_state_that_its_commit_describes(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    snapshot = reader.get_repo(BOB_DID)

    assert snapshot.head.rev == snapshot.commit.rev == network.repos[(SPACE, BOB_DID)].rev
    assert snapshot.head.state == RepoCommit.from_records(snapshot.records).state
    assert hashlib.sha256(snapshot.head.state).digest() == snapshot.commit.data
    assert 'state' not in repr(snapshot.head)


def test_snapshot_of_an_empty_repo(network: FakeSpaceNetwork) -> None:
    network.repos[(SPACE, BOB_DID)] = Repo(rev=_OLD_REV)
    reader = make_reader(network)

    snapshot = reader.get_repo(BOB_DID)

    assert snapshot.records == []
    assert snapshot.head == RepoHead(_OLD_REV, bytes(LTHASH_STATE_SIZE))
    assert snapshot.commit.data == _EMPTY_DIGEST


def test_snapshot_holds_the_records_as_decoded_from_dag_cbor(network: FakeSpaceNetwork) -> None:
    value = {
        '$type': _NOTE,
        'image': {'$type': 'blob', 'ref': {'$link': _OTHER_BLOB_CID}, 'mimeType': 'image/png', 'size': 5},
        'digest': {'$bytes': 'AQIDBAU'},
        'langs': None,
    }
    cid = network.put_record(SPACE, ALICE_DID, _NOTE, 'a', value)
    reader = make_reader(network)

    snapshot = reader.get_repo(ALICE_DID)

    assert snapshot.records == [
        RepoRecord(
            _NOTE,
            'a',
            cid,
            {
                '$type': _NOTE,
                'image': {'$type': 'blob', 'ref': CID(_OTHER_BLOB_CID), 'mimeType': 'image/png', 'size': 5},
                'digest': bytes([1, 2, 3, 4, 5]),
                'langs': None,
            },
        )
    ]


def test_list_repo_ops_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    page = reader.list_repo_ops(BOB_DID)

    request = network.requests_to(_LIST_REPO_OPS)[0]
    key_share = _key_shares(network, _LIST_REPO_OPS)[0]
    records = network.repos[(SPACE, BOB_DID)].records
    assert isinstance(page, models.ComAtprotoSpaceListRepoOps.Response)
    assert page.commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert page.cursor is None
    assert [(op.collection, op.rkey, op.cid, op.prev, op.value) for op in page.ops] == [
        (_NOTE, 'kept', records[f'{_NOTE}/kept'].cid, None, DotDict(_note('kept'))),
        (_NOTE, 'updated', records[f'{_NOTE}/updated'].cid, None, DotDict(_note('before'))),
    ]
    assert page.ops[0].rev < page.ops[1].rev == page.commit.rev
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200), (BOB_PDS, _LIST_REPO_OPS, 200)]
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert request.headers['accept-signature'] == (
        f'mac=("atproto-space-commit";sf);keyid="{key_share}";tag="atproto-space-commit"'
    )


def test_list_repo_ops_passes_its_arguments(network: FakeSpaceNetwork) -> None:
    rev = network.repos[(SPACE, BOB_DID)].ops[0].rev
    reader = make_reader(network)

    page = reader.list_repo_ops(BOB_DID, since=_OLD_REV, limit=1, cursor=f'{rev}/0', exclude_values=True)

    assert [(op.rkey, op.value) for op in page.ops] == [('updated', None)]
    assert page.cursor == f'{page.ops[0].rev}/0'
    assert dict(network.requests_to(_LIST_REPO_OPS)[0].url.params) == {
        'space': SPACE,
        'repo': BOB_DID,
        'since': _OLD_REV,
        'limit': '1',
        'cursor': f'{rev}/0',
        'excludeValues': 'true',
    }


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L385-L425
@pytest.mark.parametrize('knob', ['drop_mac', 'corrupt_mac'])
@pytest.mark.parametrize(('nsid', 'read', 'message'), _MAC_READS)
def test_response_without_a_valid_mac_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str, knob: str
) -> None:
    setattr(network, knob, True)
    resolver = FakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} {message}') as error:
        read(reader)

    first, second = _key_shares(network, nsid)
    assert isinstance(error.value.__cause__, SpaceMacError)
    assert network.statuses(nsid) == [200, 200]
    assert network.count(_AUTHORIZE) == 1
    assert first != second
    assert resolver.did.calls == [
        (BOB_DID, False),
        (BOB_DID, False),
        (AUTHORITY_DID, False),
        (BOB_DID, True),
        (BOB_DID, False),
    ]


@pytest.mark.parametrize(('nsid', 'read', 'message'), _MAC_READS)
def test_rejected_credential_is_renewed_and_the_read_retried(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str
) -> None:
    reader = make_reader(network)
    reader.authorize()
    network.revoke_credentials()

    read(reader)

    rejected, retried = _key_shares(network, nsid)
    assert network.count(_AUTHORIZE) == 2
    assert network.statuses(nsid) == [401, 200]
    assert rejected != retried


@pytest.mark.parametrize(('nsid', 'read', 'message'), _MAC_READS)
def test_account_without_a_kem_key_costs_no_request(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str
) -> None:
    network.accounts[BOB_DID].kem_key = None
    reader = make_reader(network)

    with pytest.raises(SpaceIdentityError, match=f'DID document of {BOB_DID} has no usable #atproto_kem key'):
        read(reader)

    assert network.requests == []


def _replace_record(pairs: _Pairs) -> None:
    pairs[0] = (pairs[0][0], encode_json_value(_note('changed')))


def _remove_record(pairs: _Pairs) -> None:
    del pairs[0]


def _add_record(pairs: _Pairs) -> None:
    pairs.append((f'{_NOTE}/zz', encode_json_value(_note('added'))))


def _swap_records(pairs: _Pairs) -> None:
    pairs.reverse()


def _rename_record(pairs: _Pairs) -> None:
    pairs[0] = ('note/kept', pairs[0][1])


def _break_record(pairs: _Pairs) -> None:
    pairs[0] = (pairs[0][0], b'\xff')


@pytest.mark.parametrize(
    ('tamper', 'reason'),
    [
        pytest.param(_replace_record, 'Records do not match the commit data', id='replaced'),
        pytest.param(_remove_record, 'Records do not match the commit data', id='removed'),
        pytest.param(_add_record, 'Records do not match the commit data', id='added'),
        pytest.param(_swap_records, f'Records out of order at {_NOTE}/kept', id='order'),
        pytest.param(_rename_record, 'Invalid NSID in record path: note/kept', id='path'),
        pytest.param(_break_record, f'Invalid record at {_NOTE}/kept', id='value'),
    ],
)
def test_repo_archive_changed_by_the_host_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, tamper: t.Callable[[_Pairs], None], reason: str
) -> None:
    network.tamper_archive = tamper
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification') as error:
        reader.get_repo(BOB_DID)

    assert str(error.value.__cause__) == reason
    assert network.statuses(_GET_REPO) == [200, 200]


@pytest.mark.parametrize(
    ('changes', 'reason'),
    [
        pytest.param({'ver': 2}, 'Unsupported commit version: 2', id='version'),
        pytest.param({'repo': ALICE_DID}, f'Commit is for another repo: {ALICE_DID}', id='repo'),
        pytest.param({'space': f'{SPACE}2'}, f'Commit is for another space: {SPACE}2', id='space'),
        pytest.param({'rev': '3kbcq3p7ad400'}, 'Commit revision is not a TID: 3kbcq3p7ad400', id='malformed-rev'),
        pytest.param({'rev': _OLD_REV}, 'Commit does not match its MAC', id='rev'),
        pytest.param({'data': {'$bytes': 'A' * 43}}, 'Commit does not match its MAC', id='data'),
    ],
)
def test_commit_of_the_operation_log_changed_by_the_host_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, changes: t.Dict[str, t.Any], reason: str
) -> None:
    network.tamper_ops = lambda page: page['commit'].update(changes)
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification') as error:
        reader.list_repo_ops(BOB_DID)

    assert str(error.value.__cause__) == reason
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


@pytest.mark.parametrize(
    ('changes', 'reason'),
    [
        pytest.param({'ver': 2}, 'Unsupported commit version: 2', id='version'),
        pytest.param({'repo': ALICE_DID}, f'Commit is for another repo: {ALICE_DID}', id='repo'),
        pytest.param({'space': f'{SPACE}2'}, f'Commit is for another space: {SPACE}2', id='space'),
        pytest.param({'rev': '3kbcq3p7ad400'}, 'Commit revision is not a TID: 3kbcq3p7ad400', id='rev'),
        pytest.param({'data': b'\x01' * 31}, 'Commit data must be 32 bytes, got 31', id='data'),
    ],
)
@pytest.mark.parametrize(('nsid', 'read', 'message'), _MAC_READS)
def test_malformed_commit_that_the_host_vouches_for_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str, changes: t.Dict[str, t.Any], reason: str
) -> None:
    network.tamper_commit = lambda commit: commit.update(changes)
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} {message}') as error:
        read(reader)

    assert str(error.value.__cause__) == reason
    assert network.statuses(nsid) == [200, 200]


@pytest.mark.parametrize(
    'response',
    [
        pytest.param(httpx.Response(200, json={}), id='json'),
        pytest.param(httpx.Response(200, content=b'*l\x01\x00', headers={'content-type': 'text/plain'}), id='cut'),
        pytest.param(httpx.Response(200, content=b''), id='empty'),
    ],
)
def test_response_that_is_not_a_repo_archive_is_not_retried(
    network: FakeSpaceNetwork, response: httpx.Response
) -> None:
    network.forced_responses[_GET_REPO] = [response]
    reader = make_reader(network)

    with pytest.raises(InvalidStarError, match='STAR file'):
        reader.get_repo(BOB_DID)

    assert network.count(_GET_REPO) == 1


def test_malformed_page_of_the_operation_log_is_not_retried(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_REPO_OPS] = [httpx.Response(200, json={'ops': []})]
    reader = make_reader(network)

    with pytest.raises(ModelError):
        reader.list_repo_ops(BOB_DID)

    assert network.count(_LIST_REPO_OPS) == 1


def test_error_of_the_host_is_not_retried(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(BadRequestError, match='RepoNotFound'):
        reader.get_repo(ALICE_DID)
    with pytest.raises(BadRequestError, match='RepoNotFound'):
        reader.list_repo_ops(ALICE_DID)
    with pytest.raises(BadRequestError, match='InvalidCursor'):
        reader.list_repo_ops(BOB_DID, cursor='not-a-cursor')

    assert network.statuses(_GET_REPO) == [400]
    assert network.statuses(_LIST_REPO_OPS) == [400, 400]


def test_reads_of_a_repo_require_the_repo(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = RepoHead(_OLD_REV, bytes(LTHASH_STATE_SIZE))

    with pytest.raises(ValueError, match='repo to read is required'):
        reader.get_repo()
    with pytest.raises(ValueError, match='repo to read is required'):
        reader.list_repo_ops()
    with pytest.raises(ValueError, match='repo to read is required'):
        reader.sync_repo(head, _no_records)
    with pytest.raises(ValueError, match='repo to read is required'):
        reader.pull_repo()

    assert network.requests == []


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L486-L542
def test_repo_is_pulled_in_full_and_then_from_its_known_state(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    snapshot = reader.pull_repo(repo=BOB_DID)
    assert isinstance(snapshot, RepoSnapshot)
    assert [record.rkey for record in snapshot.records] == ['kept', 'updated']

    _write_after_the_snapshot(network)
    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    records = network.repos[(SPACE, BOB_DID)].records
    assert isinstance(pulled, RepoChanges)
    assert pulled.changes == [
        RecordChange(_NOTE, 'updated', records[f'{_NOTE}/updated'].cid, snapshot.records[1].cid, _note('after')),
        RecordChange(_NOTE, 'created', records[f'{_NOTE}/created'].cid, None, _note('created')),
    ]
    assert pulled.commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert pulled.head == reader.get_repo(BOB_DID).head
    assert pulled.head != snapshot.head
    assert [nsid for _, nsid, _ in network.log] == [_AUTHORIZE, _GET_REPO, _LIST_REPO_OPS, _GET_REPO]
    assert network.requests_to(_LIST_REPO_OPS)[0].url.params['since'] == snapshot.head.rev


def test_first_pull_reads_the_repo_in_full_without_the_lookup(network: FakeSpaceNetwork) -> None:
    calls: t.List[t.Tuple[str, str]] = []

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        calls.append((collection, rkey))
        return None

    reader = make_reader(network)

    snapshot = reader.pull_repo(None, lookup, BOB_DID)

    assert isinstance(snapshot, RepoSnapshot)
    assert [record.rkey for record in snapshot.records] == ['kept', 'updated']
    assert calls == []
    assert network.count(_LIST_REPO_OPS) == 0
    assert network.count(_GET_REPO) == 1


def test_sync_of_a_repo_that_did_not_change(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert synced == RepoChanges(snapshot.commit, snapshot.head, [])
    assert reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID) == synced
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]
    assert network.count(_GET_REPO) == 1


def test_sync_from_the_empty_state_replays_the_whole_operation_log(network: FakeSpaceNetwork) -> None:
    _write_after_the_snapshot(network)
    reader = make_reader(network)
    head = RepoHead(_OLD_REV, bytes(LTHASH_STATE_SIZE))

    synced = reader.sync_repo(head, _no_records, BOB_DID)

    assert [(change.rkey, change.prev, change.value) for change in synced.changes] == [
        ('kept', None, _note('kept')),
        ('updated', None, _note('after')),
        ('created', None, _note('created')),
    ]
    assert synced.head == reader.get_repo(BOB_DID).head


def test_sync_reports_a_deleted_record_without_a_value(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    network.delete_record(SPACE, BOB_DID, _NOTE, 'kept')

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert synced.changes == [RecordChange(_NOTE, 'kept', None, snapshot.records[0].cid)]
    assert synced.head == reader.get_repo(BOB_DID).head


def test_sync_reports_one_change_of_a_record_that_changed_many_times(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'updated', 'again')
    network.delete_record(SPACE, BOB_DID, _NOTE, 'updated')
    cid = _put_note(network, BOB_DID, 'updated', 'after')
    lookups: t.List[t.Tuple[str, str]] = []

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        lookups.append((collection, rkey))
        return _lookup(snapshot)(collection, rkey)

    synced = reader.sync_repo(snapshot.head, lookup, BOB_DID)

    assert synced.changes == [RecordChange(_NOTE, 'updated', cid, snapshot.records[1].cid, _note('after'))]
    assert lookups == [(_NOTE, 'updated')]
    assert network.count(_GET_RECORD) == 0


def test_sync_holds_the_values_as_decoded_from_dag_cbor(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    value = {'$type': _NOTE, 'ref': {'$link': _OTHER_BLOB_CID}, 'digest': {'$bytes': 'AQIDBAU'}, 'langs': None}
    network.put_record(SPACE, BOB_DID, _NOTE, 'created', value)

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [change.value for change in synced.changes] == [
        {'$type': _NOTE, 'ref': CID(_OTHER_BLOB_CID), 'digest': bytes([1, 2, 3, 4, 5]), 'langs': None}
    ]
    assert synced.changes[0].value == reader.get_repo(BOB_DID).records[0].value


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L146-L166
def test_sync_follows_the_cursor(network: FakeSpaceNetwork) -> None:
    network.ops_limit = 2
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    for rkey in ['a', 'b', 'c', 'd', 'e']:
        _put_note(network, BOB_DID, rkey)

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    revs = [op.rev for op in network.repos[(SPACE, BOB_DID)].ops[2:]]
    assert [change.rkey for change in synced.changes] == ['a', 'b', 'c', 'd', 'e']
    assert synced.head == reader.get_repo(BOB_DID).head
    assert [request.url.params.get('cursor') for request in network.requests_to(_LIST_REPO_OPS)] == [
        None,
        f'{revs[1]}/0',
        f'{revs[3]}/0',
    ]
    assert {request.url.params['since'] for request in network.requests_to(_LIST_REPO_OPS)} == {snapshot.head.rev}


def test_sync_stops_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    def repeat_the_cursor(page: _Page) -> None:
        if network.count(_LIST_REPO_OPS) < _MAX_PAGES:
            page['cursor'] = _LATE_CURSOR

    network.tamper_ops = repeat_the_cursor
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [change.rkey for change in synced.changes] == ['updated', 'created']
    assert [request.url.params.get('cursor') for request in network.requests_to(_LIST_REPO_OPS)] == [None, _LATE_CURSOR]


def test_pull_stops_on_a_page_without_operations(network: FakeSpaceNetwork) -> None:
    cursors = [_LATE_CURSOR, '7zzzzzzzzzzzz/1']

    def alternate_the_cursors(page: _Page) -> None:
        count = network.count(_LIST_REPO_OPS)
        if count < _MAX_PAGES:
            page['ops'].clear()
            page['cursor'] = cursors[count % 2]

    network.tamper_ops = alternate_the_cursors
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)

    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert pulled.head == reader.get_repo(BOB_DID).head
    assert network.count(_LIST_REPO_OPS) == 1


def test_sync_stops_when_the_host_cycles_the_cursors(network: FakeSpaceNetwork) -> None:
    network.ops_limit = 1
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    for rkey in ['a', 'b', 'c']:
        _put_note(network, BOB_DID, rkey)

    revs = [op.rev for op in network.repos[(SPACE, BOB_DID)].ops[2:]]

    def cycle_the_cursors(page: _Page) -> None:
        if page.get('cursor') == f'{revs[2]}/0':
            page['cursor'] = f'{revs[0]}/0'

    network.tamper_ops = cycle_the_cursors

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [change.rkey for change in synced.changes] == ['a', 'b', 'c']
    assert [request.url.params.get('cursor') for request in network.requests_to(_LIST_REPO_OPS)] == [
        None,
        f'{revs[0]}/0',
        f'{revs[1]}/0',
    ]


def test_sync_matches_the_commit_of_the_last_page(network: FakeSpaceNetwork) -> None:
    network.ops_limit = 1
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'a')

    def write_during_the_sync(page: _Page) -> None:
        if len(network.repos[(SPACE, BOB_DID)].ops) == 3:
            _put_note(network, BOB_DID, 'b')

    network.tamper_ops = write_during_the_sync

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [change.rkey for change in synced.changes] == ['a', 'b']
    assert synced.commit.rev == network.repos[(SPACE, BOB_DID)].rev
    assert synced.head == reader.get_repo(BOB_DID).head


def test_sync_gets_the_records_that_are_listed_without_a_value(network: FakeSpaceNetwork) -> None:
    network.tamper_ops = _drop_values
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.delete_record(SPACE, BOB_DID, _NOTE, 'kept')

    synced = reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [(change.rkey, change.value) for change in synced.changes] == [
        ('updated', _note('after')),
        ('created', _note('created')),
        ('kept', None),
    ]
    assert [request.url.params['rkey'] for request in network.requests_to(_GET_RECORD)] == ['updated', 'created']
    assert synced.head == reader.get_repo(BOB_DID).head


def test_sync_of_a_record_that_changes_while_it_is_synced(network: FakeSpaceNetwork) -> None:
    def change_after_the_listing(page: _Page) -> None:
        _drop_values(page)
        _put_note(network, BOB_DID, 'updated', 'later')

    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'updated', 'after')
    network.tamper_ops = change_after_the_listing

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} changed while syncing'):
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert network.count(_GET_RECORD) == 1


def test_sync_of_a_record_that_is_not_a_map_fails_verification(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    network.put_record(SPACE, BOB_DID, _NOTE, 'updated', {'$link': _OTHER_CID})
    network.tamper_ops = _drop_values

    with pytest.raises(SpaceRepoVerificationError, match=f'Record {_NOTE}/updated failed verification') as error:
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert not isinstance(error.value, ValueError)
    assert network.statuses(_GET_RECORD) == [200]
    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification'):
        reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)


def _swap_first_ops(page: _Page) -> None:
    page['ops'][:2] = reversed(page['ops'][:2])


def _drop_op(index: int) -> t.Callable[[_Page], None]:
    def drop(page: _Page) -> None:
        del page['ops'][index]

    return drop


def _repeat_last_op(page: _Page) -> None:
    page['ops'].append(page['ops'][-1])


def _add_op(page: _Page) -> None:
    value = _note('added')
    cid = get_record_cid(encode_json_value(value))
    page['ops'].append({**page['ops'][-1], 'rkey': 'added', 'cid': cid, 'prev': None, 'value': value})


@pytest.mark.parametrize(
    ('tamper', 'reason'),
    [
        pytest.param(_swap_first_ops, 'operations are out of order', id='swapped'),
        pytest.param(_edit_op(0, rev=_OLD_REV), 'operations are out of order', id='old'),
        pytest.param(_drop_op(0), 'diverged from its commit', id='update-dropped'),
        pytest.param(_drop_op(2), f'diverged at {_NOTE}/transient', id='creation-dropped'),
        pytest.param(_repeat_last_op, f'diverged at {_NOTE}/transient', id='repeated'),
        pytest.param(_add_op, 'diverged from its commit', id='added'),
        pytest.param(_edit_op(0, prev=None), f'diverged at {_NOTE}/updated', id='prev'),
        pytest.param(_edit_op(1, prev=_OTHER_CID), f'diverged at {_NOTE}/created', id='prev-of-a-creation'),
        pytest.param(_edit_op(0, cid=None, value=None), 'diverged from its commit', id='cid'),
    ],
)
def test_sync_of_a_tampered_operation_log_fails_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, tamper: t.Callable[[_Page], None], reason: str
) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.tamper_ops = tamper

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} {reason}'):
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert [(record.rkey, record.value) for record in pulled.records] == [
        ('created', _note('created')),
        ('kept', _note('kept')),
        ('updated', _note('after')),
    ]
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]
    assert network.count(_GET_REPO) == 2


def test_operation_of_the_known_revision_is_out_of_order(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'updated', 'after')
    network.tamper_ops = _edit_op(0, rev=snapshot.head.rev)

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} operations are out of order'):
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L562-L590
def test_diverged_known_state_is_replaced_by_the_repo_in_full(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = reader.get_repo(BOB_DID).head
    _put_note(network, BOB_DID, 'updated', 'after')

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} diverged at {_NOTE}/updated'):
        reader.sync_repo(head, _no_records, BOB_DID)

    pulled = reader.pull_repo(head, _no_records, BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert [record.value for record in pulled.records] == [_note('kept'), _note('after')]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L318-L342
def test_cleared_repo_is_pulled_in_full(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    repo = network.repos[(SPACE, BOB_DID)]
    network.repos[(SPACE, BOB_DID)] = Repo(rev=f'{repo.rev[:-1]}z')

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} diverged from its commit'):
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert pulled.records == []
    assert pulled.head == RepoHead(f'{repo.rev[:-1]}z', bytes(LTHASH_STATE_SIZE))


@pytest.mark.parametrize(
    'changes',
    [
        pytest.param({'rkey': 'a' * 600}, id='long-rkey'),
        pytest.param({'rkey': '..'}, id='dots'),
        pytest.param({'rkey': 'a/b'}, id='slash'),
        pytest.param({'rkey': ''}, id='empty-rkey'),
        pytest.param({'collection': 'note'}, id='collection'),
        pytest.param({'collection': f'{_NOTE}/a'}, id='collection-path'),
        pytest.param({'rev': 'not-a-tid'}, id='rev'),
        pytest.param({'rev': '3kbcq3p7ad400'}, id='rev-alphabet'),
        pytest.param({'cid': 'bafyreinotacid'}, id='malformed-cid'),
        pytest.param({'cid': _OTHER_BLOB_CID}, id='raw-cid'),
        pytest.param({'cid': ''}, id='empty-cid'),
        pytest.param({'prev': _OTHER_CID.upper()}, id='upper-case-prev'),
        pytest.param({'prev': 'b' * 4096}, id='long-prev'),
    ],
)
def test_operation_of_a_wrong_format_fails_verification_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, changes: t.Dict[str, t.Any]
) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.tamper_ops = _edit_op(1, **changes)
    lookups: t.List[str] = []

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        lookups.append(rkey)
        return _lookup(snapshot)(collection, rkey)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} returned an invalid operation') as error:
        reader.sync_repo(snapshot.head, lookup, BOB_DID)

    pulled = reader.pull_repo(snapshot.head, lookup, BOB_DID)

    assert not isinstance(error.value, ValueError)
    assert isinstance(pulled, RepoSnapshot)
    assert [record.rkey for record in pulled.records] == ['created', 'kept', 'updated']
    assert lookups == ['updated', 'updated']
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


def _link_value(page: _Page) -> None:
    value = {'$link': _OTHER_CID}
    page['ops'][0].update(cid=get_record_cid(encode_json_value(value)), value=value)


@pytest.mark.parametrize(
    'tamper',
    [
        pytest.param(_edit_op(0, value=_note('other')), id='value'),
        pytest.param(_edit_op(0, value={**_note('after'), 'extra': None}), id='field'),
        pytest.param(_edit_op(0, value={**_note('after'), 'score': 1.5}), id='float'),
        pytest.param(_edit_op(0, cid=_OTHER_CID), id='cid'),
        pytest.param(_edit_op(0, cid=None), id='deletion'),
        pytest.param(_link_value, id='link'),
    ],
)
def test_operation_with_a_value_of_another_cid_fails_verification(
    network: FakeSpaceNetwork, tamper: t.Callable[[_Page], None]
) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'updated', 'after')
    network.tamper_ops = tamper

    with pytest.raises(SpaceRepoVerificationError, match=f'Record {_NOTE}/updated failed verification') as error:
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert not isinstance(error.value, ValueError)
    assert isinstance(pulled, RepoSnapshot)
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


@pytest.mark.parametrize('body', [b'{', b'[' * 250 + b']' * 250], ids=['cut-short', 'nested-too-deep'])
def test_operation_log_that_is_not_json_fails_verification_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, body: bytes
) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    headers = {'content-type': 'application/json'}
    network.forced_responses[_LIST_REPO_OPS] = [httpx.Response(200, content=body, headers=headers) for _ in range(2)]

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification') as error:
        reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(error.value.__cause__, RequestException)
    assert isinstance(pulled, RepoSnapshot)
    assert [record.rkey for record in pulled.records] == ['created', 'kept', 'updated']
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L544-L560
def test_repo_that_its_host_does_not_have_is_pulled_as_none(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = reader.get_repo(BOB_DID).head

    assert reader.pull_repo(repo=ALICE_DID) is None
    assert reader.pull_repo(head, _no_records, ALICE_DID) is None
    assert [nsid for _, nsid, status in network.log if status == 400] == [_GET_REPO, _LIST_REPO_OPS]


@pytest.mark.parametrize('body', [{'error': 'RepoNotFound', 'message': 'Gone'}, {'error': 'RepoNotFound'}])
def test_repo_that_is_gone_after_a_failed_sync_is_pulled_as_none(
    network: FakeSpaceNetwork, body: t.Dict[str, str]
) -> None:
    reader = make_reader(network)
    head = reader.get_repo(BOB_DID).head
    _put_note(network, BOB_DID, 'updated', 'after')
    network.forced_responses[_GET_REPO] = [httpx.Response(400, json=body)]

    assert reader.pull_repo(head, _no_records, BOB_DID) is None
    assert network.statuses(_LIST_REPO_OPS) == [200]


def test_repo_that_is_older_than_its_known_state_is_not_pulled(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    network.repos[(SPACE, BOB_DID)] = Repo(rev=_OLD_REV)

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} is older than its known state'):
        reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert network.statuses(_LIST_REPO_OPS) == [200]
    assert network.count(_GET_REPO) == 2
    assert isinstance(reader.pull_repo(repo=BOB_DID), RepoSnapshot)


def test_known_state_of_other_records_is_replaced_by_the_repo_of_the_same_revision(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = reader.get_repo(BOB_DID)
    head = RepoHead(snapshot.head.rev, bytes(LTHASH_STATE_SIZE))

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} diverged from its commit'):
        reader.sync_repo(head, _no_records, BOB_DID)

    assert reader.pull_repo(head, _no_records, BOB_DID) == snapshot


def test_pull_from_a_known_state_requires_the_lookup(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = RepoHead(_OLD_REV, bytes(LTHASH_STATE_SIZE))

    with pytest.raises(ValueError, match='lookup of the known records is required'):
        reader.pull_repo(head, repo=BOB_DID)

    assert network.requests == []


def test_pull_does_not_hide_other_errors(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = reader.get_repo(BOB_DID).head
    network.accounts[BOB_DID].unavailable = 'RepoTakendown'

    with pytest.raises(BadRequestError, match='RepoTakendown'):
        reader.pull_repo(head, _no_records, BOB_DID)
    with pytest.raises(BadRequestError, match='RepoTakendown'):
        reader.pull_repo(repo=BOB_DID)

    network.accounts[BOB_DID].unavailable = None
    network.drop_mac = True
    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification'):
        reader.pull_repo(head, _no_records, BOB_DID)


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L446-L462
def test_all_records_of_every_writer(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, ALICE_DID, 'a', 'from alice')
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [(record.repo, record.rkey, record.valid) for record in records] == [
        (BOB_DID, 'kept', True),
        (BOB_DID, 'updated', True),
        (ALICE_DID, 'a', True),
    ]
    assert (records[2].collection, records[2].cid, records[2].error) == (_NOTE, cid, None)
    assert records[2].value == DotDict(_note('from alice'))
    assert [(origin, nsid) for origin, nsid, _ in network.log] == [
        (AUTHORITY_PDS, _AUTHORIZE),
        (AUTHORITY_PDS, _LIST_WRITERS),
        (AUTHORITY_PDS, _LIST_WRITERS),
        (BOB_PDS, _GET_REPO),
        (ALICE_PDS, _GET_REPO),
    ]


def test_value_without_a_model_is_listed_in_the_json_form_and_read_in_full_as_decoded_from_dag_cbor(
    network: FakeSpaceNetwork,
) -> None:
    value = {
        '$type': _NOTE,
        'image': {'$type': 'blob', 'ref': {'$link': _OTHER_BLOB_CID}, 'mimeType': 'image/png', 'size': 5},
        'digest': {'$bytes': 'AQIDBAU'},
    }
    network.put_record(SPACE, ALICE_DID, _NOTE, 'a', value)
    reader = make_reader(network)

    listed = list(reader.records(ALICE_DID))
    read = [record for record in reader.all_records() if record.repo == ALICE_DID]

    assert [record.value for record in listed] == [DotDict(value)]
    assert [record.value for record in read] == [
        DotDict(
            {
                '$type': _NOTE,
                'image': {'$type': 'blob', 'ref': CID(_OTHER_BLOB_CID), 'mimeType': 'image/png', 'size': 5},
                'digest': bytes([1, 2, 3, 4, 5]),
            }
        )
    ]


def test_all_records_reads_the_repos_one_by_one(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    reader = make_reader(network)

    records = reader.all_records()

    assert network.requests == []
    assert next(records).repo == BOB_DID
    assert network.count(_GET_REPO) == 1
    assert [record.repo for record in records] == [BOB_DID, ALICE_DID]
    assert network.count(_GET_REPO) == 2


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L464-L476
def test_all_records_skips_a_repo_that_was_removed_from_the_space(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.remove_writer(SPACE, BOB_DID)
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [record.repo for record in records] == [ALICE_DID]
    assert [request.url.params['repo'] for request in network.requests_to(_GET_REPO)] == [ALICE_DID]


@pytest.mark.parametrize('error', ['RepoTakendown', 'RepoSuspended', 'RepoDeactivated'])
def test_all_records_skips_a_repo_that_is_not_available(network: FakeSpaceNetwork, error: str) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.accounts[BOB_DID].unavailable = error
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [record.repo for record in records] == [ALICE_DID]
    assert network.statuses(_GET_REPO) == [400, 200]


def test_all_records_skips_a_repo_that_its_host_does_not_have(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    del network.repos[(SPACE, BOB_DID)]
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [record.repo for record in records] == [ALICE_DID]
    assert network.statuses(_GET_REPO) == [400, 200]


def test_all_records_skips_a_repo_whose_error_has_no_message(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.forced_responses[_GET_REPO] = [httpx.Response(400, json={'error': 'RepoDeactivated'})]
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [record.repo for record in records] == [ALICE_DID]
    assert network.statuses(_GET_REPO) == [400, 200]


def test_all_records_does_not_hide_other_errors(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.forced_responses[_GET_REPO] = [httpx.Response(400, json={'error': 'SpaceNotFound', 'message': 'Gone'})]
    reader = make_reader(network)

    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        list(reader.all_records())

    assert network.count(_GET_REPO) == 1


def test_all_records_of_a_repo_that_fails_after_another(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.accounts[ALICE_DID].unavailable = 'SpaceNotFound'
    reader = make_reader(network)

    records = reader.all_records()

    assert [next(records).rkey for _ in range(2)] == ['kept', 'updated']
    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        next(records)

    assert network.statuses(_GET_REPO) == [200, 400]


def test_all_records_of_a_repo_that_fails_verification(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.tamper_archive = _remove_record
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification'):
        list(reader.all_records())

    assert [request.url.params['repo'] for request in network.requests_to(_GET_REPO)] == [BOB_DID, BOB_DID]


def test_all_records_reads_each_repo_once_as_its_last_entry_lists_it(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    writer = network.spaces[SPACE].writers[BOB_DID]
    write = {'repoRev': writer.repo_rev, 'data': {'$bytes': 'AAAA'}, 'spaceRev': writer.space_rev}
    repos = [
        {'$type': _REPO_WRITE, 'repo': BOB_DID, **write},
        {'$type': 'com.atproto.space.defs#repoRemoved', 'repo': ALICE_DID, 'spaceRev': writer.space_rev},
        {'$type': 'com.atproto.space.defs#repoMoved', 'repo': AUTHORITY_DID, 'spaceRev': writer.space_rev},
        {'$type': _REPO_WRITE, 'repo': ALICE_DID, **write},
        {'$type': _REPO_WRITE, 'repo': BOB_DID, **write},
    ]
    network.forced_responses[_LIST_WRITERS] = [httpx.Response(200, json={'repos': repos})]
    reader = make_reader(network)

    records = list(reader.all_records())

    assert [(record.repo, record.rkey) for record in records] == [
        (BOB_DID, 'kept'),
        (BOB_DID, 'updated'),
        (ALICE_DID, 'a'),
    ]
    assert network.count(_GET_REPO) == 2


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L319-L340
def test_all_records_are_validated_against_the_type_of_the_space(network: FakeSpaceNetwork) -> None:
    post = {'$type': _POST, 'text': 'hello', 'createdAt': '2026-11-20T00:00:00.000Z'}
    network.put_record(SPACE, ALICE_DID, _POST, 'valid', post)
    network.put_record(SPACE, ALICE_DID, _POST, 'invalid', {'$type': _POST})
    network.put_record(SPACE, ALICE_DID, _POST, 'misplaced', _note('misplaced'))
    network.put_record(SPACE, ALICE_DID, _POST, 'untyped', {'text': 'untyped'})
    network.put_record(SPACE, ALICE_DID, _OTHER, 'undeclared', {'$type': _OTHER})
    reader = make_reader(network, _GROUP)

    records = {record.rkey: record for record in reader.all_records() if record.repo == ALICE_DID}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [
        ('invalid', False),
        ('misplaced', False),
        ('untyped', False),
        ('valid', True),
        ('undeclared', False),
    ]
    assert all(isinstance(record.error, ModelError) for record in records.values() if not record.valid)
    assert isinstance(records['valid'].value, models.AppBskyFeedPost.Record)
    assert records['invalid'].value == {'$type': _POST}
    assert str(records['misplaced'].error) == f'Record of type {_NOTE} is stored under collection {_POST}'
    assert str(records['untyped'].error) == 'Record has no type'
    assert str(records['undeclared'].error) == f'{_OTHER} is not a collection of com.example.group spaces'
    assert records['undeclared'].value == {'$type': _OTHER}


def test_all_records_flags_a_record_that_is_nested_too_deep(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.repos[(SPACE, ALICE_DID)].records[f'{_NOTE}/deep'] = Record(get_record_cid(_DEEP_NOTE), {}, _DEEP_NOTE)
    reader = make_reader(network)

    records = {record.rkey: record for record in reader.all_records() if record.repo == ALICE_DID}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [('a', True), ('deep', False)]
    assert isinstance(records['deep'].error, ModelError)
    assert str(records['deep'].error) == 'Record is nested too deep'


def test_all_records_parses_a_record_with_a_blob(network: FakeSpaceNetwork) -> None:
    post = {
        '$type': _POST,
        'text': 'hello',
        'createdAt': '2026-11-20T00:00:00.000Z',
        'embed': {
            '$type': 'app.bsky.embed.images',
            'images': [
                {
                    'alt': 'cat',
                    'image': {'$type': 'blob', 'ref': {'$link': _OTHER_BLOB_CID}, 'mimeType': 'image/png', 'size': 5},
                }
            ],
        },
    }
    network.put_record(SPACE, ALICE_DID, _POST, 'p', post)
    reader = make_reader(network, _GROUP)

    record = next(record for record in reader.all_records() if record.repo == ALICE_DID)

    assert record.valid
    assert isinstance(record.value, models.AppBskyFeedPost.Record)
    assert isinstance(record.value.embed, models.AppBskyEmbedImages.Main)
    assert record.value.embed.images[0].image.cid.encode() == _OTHER_BLOB_CID


def test_all_records_share_one_credential(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, AUTHORITY_DID, 'o')
    reader = make_reader(network)

    records = list(reader.all_records()) + list(reader.all_records())

    assert len(records) == 8
    assert network.count(_AUTHORIZE) == 1
    assert network.count(_GET_REPO) == 6
