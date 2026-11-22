import asyncio
import hashlib
import threading
import typing as t

import httpx
import pytest
from atproto_client import models
from atproto_client.exceptions import BadRequestError, ModelError, RequestException
from atproto_client.models.dot_dict import DotDict
from atproto_client.request import AsyncRequest
from atproto_core.cid import CID
from atproto_crypto.lthash import LTHASH_STATE_SIZE
from atproto_space import AsyncSpaceReader, RecordChange, RepoChanges, RepoHead, RepoRecord, RepoSnapshot, SpaceType
from atproto_space._data import get_record_cid
from atproto_space.async_reader import AsyncCidLookup
from atproto_space.commit import RepoCommit
from atproto_space.exceptions import RepoGapError, SpaceMacError, SpaceRepoVerificationError
from atproto_space.repo_archive import read_repo_archive

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    ALICE_PDS,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    AsyncFakeIdResolver,
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

_NOTE = 'com.example.note'
_POST = 'app.bsky.feed.post'
_GROUP = SpaceType('com.example.group', 'any', (_NOTE, _POST))

_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'
_DAN_DID = 'did:plc:dandandandandandandandan'
_ERIN_DID = 'did:plc:erinerinerinerinerinerin'
_NEW_ACCOUNTS = {
    _CAROL_DID: 'https://carol.pds.test',
    _DAN_DID: 'https://dan.pds.test',
    _ERIN_DID: 'https://erin.pds.test',
}
_WRITERS = [BOB_DID, AUTHORITY_DID, ALICE_DID, *_NEW_ACCOUNTS]

# DAG-CBOR of a note that holds 500 maps, one in another
_DEEP_NOTE = b'\xa2\x61a' + b'\xa1\x61a' * 500 + b'\x01\x65$type\x70' + _NOTE.encode()

_OLD_REV = '3jzfcijpj2z2a'
_LATE_CURSOR = '7zzzzzzzzzzzz/0'
_MAX_PAGES = 5
# CID of the record {'text': 'hello'}
_OTHER_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
# CID of the raw bytes b'hello'
_OTHER_BLOB_CID = 'bafkreibm6jg3ux5qumhcn2b3flc3tyu6dmlb4xa7u5bf44yegnrjhc4yeq'

_BATCH = 4
_LOOP_TIMEOUT = 10

_Page = t.Dict[str, t.Any]
_Read = t.Callable[[AsyncSpaceReader], t.Awaitable[object]]


def make_reader(
    network: FakeSpaceNetwork, space_type: t.Optional[SpaceType] = None, **kwargs: t.Any
) -> AsyncSpaceReader:
    kwargs.setdefault('delegation_token_provider', delegation_token_provider(network, ALICE_DID))
    kwargs.setdefault('id_resolver', AsyncFakeIdResolver(network))
    kwargs.setdefault('request', AsyncRequest(transport=network.async_transport))

    return AsyncSpaceReader(SPACE, space_type, **kwargs)


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


def _add_writers(network: FakeSpaceNetwork) -> None:
    """Let six accounts write to the space, each on its own PDS."""
    for did, pds in _NEW_ACCOUNTS.items():
        network.add_account(did, pds)
        network.spaces[SPACE].members.add(did)

    for did in _WRITERS[1:]:
        _put_note(network, did, 'a')


def _lookup(snapshot: RepoSnapshot) -> AsyncCidLookup:
    index = {(record.collection, record.rkey): record.cid for record in snapshot.records}

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        return index.get((collection, rkey))

    return lookup


def _no_records(_: str, __: str) -> t.Optional[str]:
    return None


async def _get_repo(reader: AsyncSpaceReader) -> object:
    return await reader.get_repo(BOB_DID)


async def _list_repo_ops(reader: AsyncSpaceReader) -> object:
    return await reader.list_repo_ops(BOB_DID)


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


def _drop_op(index: int) -> t.Callable[[_Page], None]:
    def drop(page: _Page) -> None:
        del page['ops'][index]

    return drop


def _swap_first_ops(page: _Page) -> None:
    page['ops'][:2] = reversed(page['ops'][:2])


def _drop_values(page: _Page) -> None:
    for op in page['ops']:
        op.pop('value', None)


def _write_after_the_snapshot(network: FakeSpaceNetwork) -> None:
    """Write to the repo the way the test of upstream does: an update, a creation, and a record that does not last."""
    _put_note(network, BOB_DID, 'updated', 'after')
    _put_note(network, BOB_DID, 'created', 'created')
    _put_note(network, BOB_DID, 'transient', 'transient')
    network.delete_record(SPACE, BOB_DID, _NOTE, 'transient')


@pytest.mark.asyncio
async def test_get_repo_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    snapshot = await reader.get_repo(BOB_DID)

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


@pytest.mark.asyncio
async def test_snapshot_holds_the_state_that_its_commit_describes(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    snapshot = await reader.get_repo(BOB_DID)

    assert snapshot.head.rev == snapshot.commit.rev == network.repos[(SPACE, BOB_DID)].rev
    assert snapshot.head.state == RepoCommit.from_records(snapshot.records).state
    assert hashlib.sha256(snapshot.head.state).digest() == snapshot.commit.data


@pytest.mark.asyncio
async def test_event_loop_runs_while_a_repo_is_verified(
    network: FakeSpaceNetwork, monkeypatch: pytest.MonkeyPatch
) -> None:
    loop = asyncio.get_running_loop()
    ran = threading.Event()
    waits: t.List[bool] = []

    def read(data: bytes) -> object:
        # the event is set by the event loop, which a verification on its thread would keep from running
        loop.call_soon_threadsafe(ran.set)
        waits.append(ran.wait(_LOOP_TIMEOUT))

        return read_repo_archive(data)

    monkeypatch.setattr('atproto_space._reader.read_repo_archive', read)
    reader = make_reader(network)

    snapshot = await reader.get_repo(BOB_DID)

    assert waits == [True]
    assert [record.rkey for record in snapshot.records] == ['kept', 'updated']


@pytest.mark.asyncio
async def test_list_repo_ops_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    rev = network.repos[(SPACE, BOB_DID)].ops[0].rev
    reader = make_reader(network)

    page = await reader.list_repo_ops(BOB_DID)
    rest = await reader.list_repo_ops(BOB_DID, since=_OLD_REV, limit=1, cursor=f'{rev}/0', exclude_values=True)

    requests = network.requests_to(_LIST_REPO_OPS)
    assert isinstance(page, models.ComAtprotoSpaceListRepoOps.Response)
    assert page.commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert [(op.rkey, op.prev, op.value) for op in page.ops] == [
        ('kept', None, DotDict(_note('kept'))),
        ('updated', None, DotDict(_note('before'))),
    ]
    assert [(op.rkey, op.value) for op in rest.ops] == [('updated', None)]
    assert dict(requests[0].url.params) == {'space': SPACE, 'repo': BOB_DID}
    assert dict(requests[1].url.params) == {
        'space': SPACE,
        'repo': BOB_DID,
        'since': _OLD_REV,
        'limit': '1',
        'cursor': f'{rev}/0',
        'excludeValues': 'true',
    }
    assert len(set(_key_shares(network, _LIST_REPO_OPS))) == 2


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L385-L425
@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read', 'message'), _MAC_READS)
async def test_response_without_a_mac_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str
) -> None:
    network.drop_mac = True
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} {message}') as error:
        await read(reader)

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


@pytest.mark.asyncio
async def test_repo_archive_changed_by_the_host_is_rejected_after_one_retry(network: FakeSpaceNetwork) -> None:
    network.tamper_archive = lambda pairs: pairs.reverse()
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification') as error:
        await reader.get_repo(BOB_DID)

    assert str(error.value.__cause__) == f'Records out of order at {_NOTE}/kept'
    assert network.statuses(_GET_REPO) == [200, 200]


@pytest.mark.asyncio
async def test_reads_of_a_repo_require_the_repo(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = RepoHead(_OLD_REV, bytes(LTHASH_STATE_SIZE))

    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.get_repo()
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.list_repo_ops()
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.sync_repo(head, _no_records)
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.pull_repo()
    with pytest.raises(ValueError, match='lookup of the known records is required'):
        await reader.pull_repo(head, repo=BOB_DID)

    assert network.requests == []


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L486-L542
@pytest.mark.asyncio
async def test_repo_is_pulled_in_full_and_then_from_its_known_state(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    snapshot = await reader.pull_repo(repo=BOB_DID)
    assert isinstance(snapshot, RepoSnapshot)
    assert [record.rkey for record in snapshot.records] == ['kept', 'updated']

    _write_after_the_snapshot(network)
    pulled = await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    records = network.repos[(SPACE, BOB_DID)].records
    assert isinstance(pulled, RepoChanges)
    assert pulled.changes == [
        RecordChange(_NOTE, 'updated', records[f'{_NOTE}/updated'].cid, snapshot.records[1].cid, _note('after')),
        RecordChange(_NOTE, 'created', records[f'{_NOTE}/created'].cid, None, _note('created')),
    ]
    assert pulled.commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert pulled.head == (await reader.get_repo(BOB_DID)).head
    assert [nsid for _, nsid, _ in network.log] == [_AUTHORIZE, _GET_REPO, _LIST_REPO_OPS, _GET_REPO]
    assert network.requests_to(_LIST_REPO_OPS)[0].url.params['since'] == snapshot.head.rev


@pytest.mark.asyncio
async def test_first_pull_reads_the_repo_in_full_without_the_lookup(network: FakeSpaceNetwork) -> None:
    calls: t.List[t.Tuple[str, str]] = []

    def lookup(collection: str, rkey: str) -> t.Optional[str]:
        calls.append((collection, rkey))
        return None

    reader = make_reader(network)

    snapshot = await reader.pull_repo(None, lookup, BOB_DID)

    assert isinstance(snapshot, RepoSnapshot)
    assert [record.rkey for record in snapshot.records] == ['kept', 'updated']
    assert calls == []
    assert network.count(_LIST_REPO_OPS) == 0
    assert network.count(_GET_REPO) == 1


@pytest.mark.asyncio
async def test_lookup_may_be_a_coroutine_function(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    cid = _put_note(network, BOB_DID, 'updated', 'after')
    lookups: t.List[t.Tuple[str, str]] = []

    async def lookup(collection: str, rkey: str) -> t.Optional[str]:
        await asyncio.sleep(0)
        lookups.append((collection, rkey))
        return snapshot.records[1].cid

    synced = await reader.sync_repo(snapshot.head, lookup, BOB_DID)

    assert synced.changes == [RecordChange(_NOTE, 'updated', cid, snapshot.records[1].cid, _note('after'))]
    assert lookups == [(_NOTE, 'updated')]


@pytest.mark.asyncio
async def test_sync_of_a_repo_that_did_not_change(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)

    synced = await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert synced == RepoChanges(snapshot.commit, snapshot.head, [])
    assert await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID) == synced
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]
    assert network.count(_GET_REPO) == 1


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L146-L166
@pytest.mark.asyncio
async def test_sync_follows_the_cursor(network: FakeSpaceNetwork) -> None:
    network.ops_limit = 2
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    for rkey in ['a', 'b', 'c', 'd', 'e']:
        _put_note(network, BOB_DID, rkey)

    synced = await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    revs = [op.rev for op in network.repos[(SPACE, BOB_DID)].ops[2:]]
    assert [change.rkey for change in synced.changes] == ['a', 'b', 'c', 'd', 'e']
    assert synced.head == (await reader.get_repo(BOB_DID)).head
    assert [request.url.params.get('cursor') for request in network.requests_to(_LIST_REPO_OPS)] == [
        None,
        f'{revs[1]}/0',
        f'{revs[3]}/0',
    ]


@pytest.mark.asyncio
async def test_pull_stops_on_a_page_without_operations(network: FakeSpaceNetwork) -> None:
    cursors = [_LATE_CURSOR, '7zzzzzzzzzzzz/1']

    def alternate_the_cursors(page: _Page) -> None:
        count = network.count(_LIST_REPO_OPS)
        if count < _MAX_PAGES:
            page['ops'].clear()
            page['cursor'] = cursors[count % 2]

    network.tamper_ops = alternate_the_cursors
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)

    pulled = await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert pulled.head == (await reader.get_repo(BOB_DID)).head
    assert network.count(_LIST_REPO_OPS) == 1


@pytest.mark.asyncio
async def test_sync_stops_when_the_host_cycles_the_cursors(network: FakeSpaceNetwork) -> None:
    network.ops_limit = 1
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    for rkey in ['a', 'b', 'c']:
        _put_note(network, BOB_DID, rkey)

    revs = [op.rev for op in network.repos[(SPACE, BOB_DID)].ops[2:]]

    def cycle_the_cursors(page: _Page) -> None:
        if page.get('cursor') == f'{revs[2]}/0':
            page['cursor'] = f'{revs[0]}/0'

    network.tamper_ops = cycle_the_cursors

    synced = await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [change.rkey for change in synced.changes] == ['a', 'b', 'c']
    assert [request.url.params.get('cursor') for request in network.requests_to(_LIST_REPO_OPS)] == [
        None,
        f'{revs[0]}/0',
        f'{revs[1]}/0',
    ]


@pytest.mark.asyncio
async def test_sync_gets_the_records_that_are_listed_without_a_value(network: FakeSpaceNetwork) -> None:
    network.tamper_ops = _drop_values
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.delete_record(SPACE, BOB_DID, _NOTE, 'kept')

    synced = await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert [(change.rkey, change.value) for change in synced.changes] == [
        ('updated', _note('after')),
        ('created', _note('created')),
        ('kept', None),
    ]
    assert [request.url.params['rkey'] for request in network.requests_to(_GET_RECORD)] == ['updated', 'created']
    assert synced.head == (await reader.get_repo(BOB_DID)).head


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('tamper', 'reason'),
    [
        pytest.param(_swap_first_ops, 'operations are out of order', id='swapped'),
        pytest.param(_drop_op(0), 'diverged from its commit', id='update-dropped'),
        pytest.param(_drop_op(2), f'diverged at {_NOTE}/transient', id='creation-dropped'),
        pytest.param(_edit_op(0, prev=None), f'diverged at {_NOTE}/updated', id='prev'),
    ],
)
async def test_sync_of_a_tampered_operation_log_fails_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, tamper: t.Callable[[_Page], None], reason: str
) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.tamper_ops = tamper

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} {reason}'):
        await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(pulled, RepoSnapshot)
    assert [(record.rkey, record.value) for record in pulled.records] == [
        ('created', _note('created')),
        ('kept', _note('kept')),
        ('updated', _note('after')),
    ]
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]
    assert network.count(_GET_REPO) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'changes',
    [
        pytest.param({'rkey': 'a' * 600}, id='long-rkey'),
        pytest.param({'collection': 'note'}, id='collection'),
        pytest.param({'rev': 'not-a-tid'}, id='rev'),
        pytest.param({'cid': 'bafyreinotacid'}, id='malformed-cid'),
        pytest.param({'prev': _OTHER_CID.upper()}, id='upper-case-prev'),
    ],
)
async def test_operation_of_a_wrong_format_fails_verification_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, changes: t.Dict[str, t.Any]
) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    network.tamper_ops = _edit_op(1, **changes)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} returned an invalid operation') as error:
        await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert not isinstance(error.value, ValueError)
    assert isinstance(pulled, RepoSnapshot)
    assert [record.rkey for record in pulled.records] == ['created', 'kept', 'updated']
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


@pytest.mark.asyncio
async def test_operation_with_a_value_of_another_cid_fails_verification(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _put_note(network, BOB_DID, 'updated', 'after')
    network.tamper_ops = _edit_op(0, value=_note('other'))

    with pytest.raises(SpaceRepoVerificationError, match=f'Record {_NOTE}/updated failed verification'):
        await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID), RepoSnapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize('body', [b'{', b'[' * 250 + b']' * 250], ids=['cut-short', 'nested-too-deep'])
async def test_operation_log_that_is_not_json_fails_verification_and_the_repo_is_pulled_in_full(
    network: FakeSpaceNetwork, body: bytes
) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    _write_after_the_snapshot(network)
    headers = {'content-type': 'application/json'}
    network.forced_responses[_LIST_REPO_OPS] = [httpx.Response(200, content=body, headers=headers) for _ in range(2)]

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification') as error:
        await reader.sync_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    pulled = await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert isinstance(error.value.__cause__, RequestException)
    assert isinstance(pulled, RepoSnapshot)
    assert [record.rkey for record in pulled.records] == ['created', 'kept', 'updated']
    assert network.statuses(_LIST_REPO_OPS) == [200, 200]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L544-L560
@pytest.mark.asyncio
async def test_repo_that_its_host_does_not_have_is_pulled_as_none(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    head = (await reader.get_repo(BOB_DID)).head

    assert await reader.pull_repo(repo=ALICE_DID) is None
    assert await reader.pull_repo(head, _no_records, ALICE_DID) is None
    assert [nsid for _, nsid, status in network.log if status == 400] == [_GET_REPO, _LIST_REPO_OPS]


@pytest.mark.asyncio
@pytest.mark.parametrize('body', [{'error': 'RepoNotFound', 'message': 'Gone'}, {'error': 'RepoNotFound'}])
async def test_repo_that_is_gone_after_a_failed_sync_is_pulled_as_none(
    network: FakeSpaceNetwork, body: t.Dict[str, str]
) -> None:
    reader = make_reader(network)
    head = (await reader.get_repo(BOB_DID)).head
    _put_note(network, BOB_DID, 'updated', 'after')
    network.forced_responses[_GET_REPO] = [httpx.Response(400, json=body)]

    assert await reader.pull_repo(head, _no_records, BOB_DID) is None
    assert network.statuses(_LIST_REPO_OPS) == [200]


@pytest.mark.asyncio
async def test_repo_that_is_older_than_its_known_state_is_not_pulled(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    snapshot = await reader.get_repo(BOB_DID)
    network.repos[(SPACE, BOB_DID)] = Repo(rev=_OLD_REV)

    with pytest.raises(RepoGapError, match=f'Repo {BOB_DID} is older than its known state'):
        await reader.pull_repo(snapshot.head, _lookup(snapshot), BOB_DID)

    assert network.statuses(_LIST_REPO_OPS) == [200]
    assert network.count(_GET_REPO) == 2


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L446-L462
@pytest.mark.asyncio
async def test_all_records_of_every_writer(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, ALICE_DID, 'a', 'from alice')
    reader = make_reader(network)

    records = [record async for record in reader.all_records()]

    assert [(record.repo, record.rkey, record.valid) for record in records] == [
        (BOB_DID, 'kept', True),
        (BOB_DID, 'updated', True),
        (ALICE_DID, 'a', True),
    ]
    assert (records[2].collection, records[2].cid, records[2].error) == (_NOTE, cid, None)
    assert records[2].value == DotDict(_note('from alice'))
    assert network.log[:3] == [
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (AUTHORITY_PDS, _LIST_WRITERS, 200),
        (AUTHORITY_PDS, _LIST_WRITERS, 200),
    ]
    assert sorted(network.log[3:]) == [(ALICE_PDS, _GET_REPO, 200), (BOB_PDS, _GET_REPO, 200)]


@pytest.mark.asyncio
async def test_value_without_a_model_is_listed_in_the_json_form_and_read_in_full_as_decoded_from_dag_cbor(
    network: FakeSpaceNetwork,
) -> None:
    value = {
        '$type': _NOTE,
        'image': {'$type': 'blob', 'ref': {'$link': _OTHER_BLOB_CID}, 'mimeType': 'image/png', 'size': 5},
        'digest': {'$bytes': 'AQIDBAU'},
    }
    network.put_record(SPACE, ALICE_DID, _NOTE, 'a', value)
    reader = make_reader(network)

    listed = [record async for record in reader.records(ALICE_DID)]
    read = [record async for record in reader.all_records() if record.repo == ALICE_DID]

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


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L464-L476
@pytest.mark.asyncio
async def test_all_records_skips_a_repo_that_was_removed_from_the_space(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.remove_writer(SPACE, BOB_DID)
    reader = make_reader(network)

    records = [record async for record in reader.all_records()]

    assert [record.repo for record in records] == [ALICE_DID]
    assert [request.url.params['repo'] for request in network.requests_to(_GET_REPO)] == [ALICE_DID]


@pytest.mark.asyncio
@pytest.mark.parametrize('error', ['RepoNotFound', 'RepoTakendown', 'RepoSuspended', 'RepoDeactivated'])
async def test_all_records_skips_a_repo_that_is_not_available(network: FakeSpaceNetwork, error: str) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.accounts[BOB_DID].unavailable = error
    reader = make_reader(network)

    records = [record async for record in reader.all_records()]

    assert [record.repo for record in records] == [ALICE_DID]
    assert sorted(network.statuses(_GET_REPO)) == [200, 400]


@pytest.mark.asyncio
async def test_all_records_skips_a_repo_whose_error_has_no_message(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_GET_REPO] = [httpx.Response(400, json={'error': 'RepoDeactivated'})]
    reader = make_reader(network)

    records = [record async for record in reader.all_records()]

    assert records == []
    assert network.statuses(_GET_REPO) == [400]


@pytest.mark.asyncio
async def test_all_records_does_not_hide_other_errors(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.accounts[BOB_DID].unavailable = 'SpaceNotFound'
    reader = make_reader(network)

    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        _ = [record async for record in reader.all_records()]


def _stalling_request(
    network: FakeSpaceNetwork, repos: t.Collection[str]
) -> t.Tuple[AsyncRequest, asyncio.Event, t.List[str]]:
    """Build an HTTP client of the network that never gets the given repos in full.

    Returns the client, the event of every one of the repos being asked for, and the repos that it gave up.
    """
    asked: t.List[str] = []
    all_asked = asyncio.Event()
    stopped: t.List[str] = []

    async def handle(request: httpx.Request) -> httpx.Response:
        repo = request.url.params.get('repo')
        if request.url.path.endswith(_GET_REPO) and repo in repos:
            asked.append(repo)
            if len(asked) == len(repos):
                all_asked.set()

            try:
                await asyncio.sleep(_LOOP_TIMEOUT)
            except asyncio.CancelledError:
                stopped.append(repo)
                raise

        return await network.handle_async(request)

    return AsyncRequest(transport=httpx.MockTransport(handle)), all_asked, stopped


@pytest.mark.asyncio
async def test_all_records_of_a_batch_of_repos_that_fails(network: FakeSpaceNetwork) -> None:
    _add_writers(network)
    network.accounts[AUTHORITY_DID].unavailable = 'SpaceNotFound'
    request, _, stopped = _stalling_request(network, {ALICE_DID, _CAROL_DID})
    reader = make_reader(network, request=request)

    records = reader.all_records()

    assert [(await records.__anext__()).rkey for _ in range(2)] == ['kept', 'updated']
    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        await records.__anext__()

    assert sorted(stopped) == sorted([ALICE_DID, _CAROL_DID])
    assert sorted(network.statuses(_GET_REPO)) == [200, 400]


@pytest.mark.asyncio
async def test_all_records_that_are_cancelled(network: FakeSpaceNetwork) -> None:
    _add_writers(network)
    request, all_asked, stopped = _stalling_request(network, {ALICE_DID, _CAROL_DID})
    reader = make_reader(network, request=request)

    async def read() -> t.List[str]:
        return [record.repo async for record in reader.all_records()]

    task = asyncio.ensure_future(read())
    await asyncio.wait_for(all_asked.wait(), _LOOP_TIMEOUT)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert sorted(stopped) == sorted([ALICE_DID, _CAROL_DID])


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L319-L340
@pytest.mark.asyncio
async def test_all_records_are_validated_against_the_type_of_the_space(network: FakeSpaceNetwork) -> None:
    post = {'$type': _POST, 'text': 'hello', 'createdAt': '2026-11-20T00:00:00.000Z'}
    network.put_record(SPACE, ALICE_DID, _POST, 'valid', post)
    network.put_record(SPACE, ALICE_DID, _POST, 'misplaced', _note('misplaced'))
    network.put_record(SPACE, ALICE_DID, 'com.example.other', 'undeclared', {'$type': 'com.example.other'})
    reader = make_reader(network, _GROUP)

    records = {record.rkey: record async for record in reader.all_records() if record.repo == ALICE_DID}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [
        ('misplaced', False),
        ('valid', True),
        ('undeclared', False),
    ]
    assert isinstance(records['valid'].value, models.AppBskyFeedPost.Record)
    assert isinstance(records['misplaced'].error, ModelError)
    assert str(records['misplaced'].error) == f'Record of type {_NOTE} is stored under collection {_POST}'
    assert str(records['undeclared'].error) == 'com.example.other is not a collection of com.example.group spaces'


@pytest.mark.asyncio
async def test_all_records_flags_a_record_that_is_nested_too_deep(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.repos[(SPACE, ALICE_DID)].records[f'{_NOTE}/deep'] = Record(get_record_cid(_DEEP_NOTE), {}, _DEEP_NOTE)
    reader = make_reader(network)

    records = {record.rkey: record async for record in reader.all_records() if record.repo == ALICE_DID}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [('a', True), ('deep', False)]
    assert isinstance(records['deep'].error, ModelError)
    assert str(records['deep'].error) == 'Record is nested too deep'


@pytest.mark.asyncio
async def test_all_records_reads_four_repos_at_a_time_with_one_credential(network: FakeSpaceNetwork) -> None:
    _add_writers(network)
    in_flight: t.List[str] = []
    peaks: t.List[int] = []
    batches = [asyncio.Event(), asyncio.Event()]

    async def handle(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith(_GET_REPO):
            return await network.handle_async(request)

        # every repo of a batch is asked for before any of them is answered
        batch = batches[len(peaks) // _BATCH]
        in_flight.append(request.url.params['repo'])
        peaks.append(len(in_flight))
        if len(peaks) in {_BATCH, len(_WRITERS)}:
            batch.set()

        await asyncio.wait_for(batch.wait(), 10)
        try:
            return await network.handle_async(request)
        finally:
            in_flight.remove(request.url.params['repo'])

    reader = make_reader(network, request=AsyncRequest(transport=httpx.MockTransport(handle)))

    records = [record async for record in reader.all_records()]

    assert [record.repo for record in records] == [BOB_DID, *_WRITERS]
    assert peaks == [1, 2, 3, 4, 1, 2]
    assert network.count(_AUTHORIZE) == 1
    assert network.statuses(_GET_REPO) == [200] * len(_WRITERS)
    assert len(reader._locks) == 0


@pytest.mark.asyncio
async def test_all_records_renews_a_credential_that_a_batch_of_repos_rejects_once(network: FakeSpaceNetwork) -> None:
    _add_writers(network)
    rejected: t.List[str] = []
    waiting: t.List[httpx.Request] = []
    sent = asyncio.Event()

    async def handle(request: httpx.Request) -> httpx.Response:
        # every repo of the batch is asked for before any of the requests learns that the credential is rejected
        if request.headers.get('authorization') in rejected:
            waiting.append(request)
            if len(waiting) == _BATCH:
                sent.set()

            await asyncio.wait_for(sent.wait(), 10)

        response = await network.handle_async(request)
        if request.url.path.endswith(_LIST_WRITERS) and not response.json()['repos']:
            rejected.append(request.headers['authorization'])
            network.revoke_credentials()

        return response

    reader = make_reader(network, request=AsyncRequest(transport=httpx.MockTransport(handle)))
    network.delays[_AUTHORIZE] = 0.05

    records = [record async for record in reader.all_records()]

    assert [record.repo for record in records] == [BOB_DID, *_WRITERS]
    assert network.count(_AUTHORIZE) == 2
    assert network.statuses(_GET_REPO) == [401] * _BATCH + [200] * len(_WRITERS)
    assert len(reader._locks) == 0
