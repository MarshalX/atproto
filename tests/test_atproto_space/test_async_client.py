import json
import typing as t

import httpx
import pytest
from atproto_client import AsyncClient, models
from atproto_client.exceptions import BadRequestError, LoginRequiredError
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.string_formats import TID_RE
from atproto_client.request import AsyncRequest
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
from atproto_space import AsyncSpaceClient, AsyncSpaceReader, RepoChanges, SpaceType
from atproto_space.exceptions import SpaceRepoVerificationError
from atproto_space.tokens import parse_space_token

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    ALICE_PDS,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    Account,
    AsyncFakeIdResolver,
    FakeAuthSession,
    FakeSpaceNetwork,
    async_fake_client,
    async_fake_id_resolver,
    async_fake_password_client,
    build_network,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_GET_DELEGATION_TOKEN = 'com.atproto.space.getDelegationToken'
_LIST_RECORDS = 'com.atproto.space.listRecords'
_LIST_BLOBS = 'com.atproto.space.listBlobs'
_GET_RECORD = 'com.atproto.space.getRecord'
_GET_LATEST_COMMIT = 'com.atproto.space.getLatestCommit'
_GET_BLOB = 'com.atproto.space.getBlob'
_GET_REPO = 'com.atproto.space.getRepo'
_LIST_REPO_OPS = 'com.atproto.space.listRepoOps'
_CREATE_RECORD = 'com.atproto.space.createRecord'
_PUT_RECORD = 'com.atproto.space.putRecord'
_DELETE_RECORD = 'com.atproto.space.deleteRecord'
_APPLY_WRITES = 'com.atproto.space.applyWrites'
_CLEAR_RECORDS = 'com.atproto.space.clearRecords'
_CREATE_SPACE = 'com.atproto.space.createSpace'

_MEMBERSPACE_POLICY = 'com.atproto.memberspace.policy'
_PERSONALSPACE_POLICY = 'com.atproto.personalspace.policy'

_NOTE = 'com.example.note'
_OTHER = 'com.example.other'
_GROUP = SpaceType('com.example.group', 'any', (_NOTE,))
_BOOKMARKS = SpaceType('com.example.bookmarks', 'literal:self')

_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'
_CAROL_PDS = 'https://carol.pds.test'

_BLOB = b'\x01\x02\x03\x04\x05'

_Login = t.Callable[[FakeSpaceNetwork, Account], t.Awaitable[AsyncClient]]
_Read = t.Callable[[AsyncSpaceClient], t.Awaitable[object]]
_Sent = t.List[httpx.Request]


def _recording_request(network: FakeSpaceNetwork) -> t.Tuple[AsyncRequest, _Sent]:
    """Build an HTTP client of the network that keeps the requests that it sends."""
    sent: _Sent = []

    async def handle(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return await network.handle_async(request)

    return AsyncRequest(transport=httpx.MockTransport(handle)), sent


async def make_client(
    network: FakeSpaceNetwork,
    did: str = BOB_DID,
    space_type: t.Optional[SpaceType] = None,
    login: _Login = async_fake_client,
    **kwargs: t.Any,
) -> AsyncSpaceClient:
    kwargs.setdefault('id_resolver', AsyncFakeIdResolver(network))
    kwargs.setdefault('request', AsyncRequest(transport=network.async_transport))

    return AsyncSpaceClient(await login(network, network.accounts[did]), SPACE, space_type, **kwargs)


@pytest.fixture
def network() -> FakeSpaceNetwork:
    return build_network()


def _note(text: str) -> t.Dict[str, t.Any]:
    return {'$type': _NOTE, 'text': text}


def _put_note(network: FakeSpaceNetwork, repo: str, rkey: str, text: str = 'hello') -> str:
    return network.put_record(SPACE, repo, _NOTE, rkey, _note(text))


def _rkey(uri: str) -> str:
    return uri.rsplit('/', 1)[1]


def _body(network: FakeSpaceNetwork, nsid: str) -> t.Dict[str, t.Any]:
    body: t.Dict[str, t.Any] = json.loads(network.requests_to(nsid)[-1].content)
    return body


def _origins(network: FakeSpaceNetwork) -> t.Set[str]:
    return {origin for origin, _, _ in network.log}


@pytest.mark.asyncio
async def test_client_of_a_space_uri(network: FakeSpaceNetwork) -> None:
    client = await async_fake_client(network, network.accounts[BOB_DID])

    space = AsyncSpaceClient(client, SPACE, _GROUP)

    assert isinstance(space, AsyncSpaceReader)
    assert space.client is client
    assert space.did == BOB_DID
    assert space.ref == SpaceRef(AUTHORITY_DID, 'com.example.group', 'main')
    assert space.uri == SPACE
    assert space.space_type is _GROUP
    assert isinstance(space.request, AsyncRequest)
    assert space.request is not client.request
    assert isinstance(space._id_resolver.did._cache, AsyncDidInMemoryCache)


@pytest.mark.asyncio
async def test_client_requires_a_login() -> None:
    with pytest.raises(LoginRequiredError):
        AsyncSpaceClient(AsyncClient(), SPACE)


@pytest.mark.asyncio
@pytest.mark.parametrize('login', [async_fake_client, async_fake_password_client], ids=['oauth', 'password'])
async def test_client_refuses_the_request_of_a_client(network: FakeSpaceNetwork, login: _Login) -> None:
    client = await login(network, network.accounts[BOB_DID])

    with pytest.raises(ValueError, match='must carry no session of an account'):
        AsyncSpaceClient(client, SPACE, request=client.request)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        AsyncSpaceClient(client, SPACE, request=client.request.clone())


@pytest.mark.asyncio
@pytest.mark.parametrize('login', [async_fake_client, async_fake_password_client], ids=['oauth', 'password'])
async def test_did_is_the_account_of_the_session(network: FakeSpaceNetwork, login: _Login) -> None:
    client = await login(network, network.accounts[ALICE_DID])

    assert client.me is None
    assert AsyncSpaceClient(client, SPACE).did == ALICE_DID


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L185-L215
@pytest.mark.asyncio
async def test_own_repo_is_read_and_written_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    request, sent = _recording_request(network)
    resolver = AsyncFakeIdResolver(network)
    space = await make_client(network, id_resolver=resolver, request=request)

    rkey = _rkey((await space.create_record(_note('new'))).uri)
    await space.put_record(_note('updated'), rkey)
    assert (await space.get_record(_NOTE, rkey)).value == _note('updated')

    await space.apply_writes(
        [
            models.ComAtprotoSpaceApplyWrites.Delete(collection=_NOTE, rkey=rkey),
            models.ComAtprotoSpaceApplyWrites.Create(collection=_NOTE, value=DotDict(_note('batched'))),
        ]
    )
    listed = await space.list_records(collection=_NOTE)
    assert [record.value for record in listed.records] == [_note('batched')]
    assert [record.value async for record in space.records()] == [_note('batched')]

    assert await space.delete_record(_NOTE, listed.records[0].rkey) is True
    await space.create_record(_note('last'))
    assert await space.clear_records() is True
    assert [record async for record in space.records(collection=_NOTE)] == []

    assert sent == []
    assert resolver.did.calls == []
    assert network.count(_AUTHORIZE) == 0
    assert network.count(_GET_DELEGATION_TOKEN) == 0
    assert _origins(network) == {BOB_PDS}
    assert all(status == 200 for _, _, status in network.log)


@pytest.mark.asyncio
async def test_writes_name_the_space_the_repo_and_the_collection(network: FakeSpaceNetwork) -> None:
    space = await make_client(network)

    created = await space.create_record(_note('a'), 'a', validate=False)
    replaced = await space.put_record(_note('b'), 'a', validate=False)
    await space.apply_writes(
        [models.ComAtprotoSpaceApplyWrites.Update(collection=_NOTE, rkey='a', value=DotDict(_note('c')))],
        validate=False,
    )
    assert await space.delete_record(_NOTE, 'a') is True
    assert await space.clear_records() is True

    target = {'space': SPACE, 'repo': BOB_DID}
    write = {**target, 'collection': _NOTE, 'rkey': 'a', 'validate': False}
    assert replaced.uri == created.uri == f'{SPACE}/{BOB_DID}/{_NOTE}/a'
    assert _body(network, _CREATE_RECORD) == {**write, 'record': _note('a')}
    assert _body(network, _PUT_RECORD) == {**write, 'record': _note('b')}
    assert _body(network, _APPLY_WRITES) == {
        **target,
        'validate': False,
        'writes': [
            {'$type': 'com.atproto.space.applyWrites#update', 'collection': _NOTE, 'rkey': 'a', 'value': _note('c')}
        ],
    }
    assert _body(network, _DELETE_RECORD) == {**target, 'collection': _NOTE, 'rkey': 'a'}
    assert _body(network, _CLEAR_RECORDS) == target


@pytest.mark.asyncio
async def test_record_without_a_type_is_not_written(network: FakeSpaceNetwork) -> None:
    space = await make_client(network)

    with pytest.raises(ValueError, match='Record has no type'):
        await space.create_record({'text': 'hello'})

    assert network.requests == []


async def _get_record(space: AsyncSpaceClient) -> object:
    return await space.get_record(_NOTE, 'a')


async def _get_latest_commit(space: AsyncSpaceClient) -> object:
    return await space.get_latest_commit()


async def _get_repo(space: AsyncSpaceClient) -> object:
    return await space.get_repo()


async def _list_repo_ops(space: AsyncSpaceClient) -> object:
    return await space.list_repo_ops()


async def _list_records(space: AsyncSpaceClient) -> object:
    return await space.list_records()


async def _list_blobs(space: AsyncSpaceClient) -> object:
    return await space.list_blobs()


async def _get_blob(space: AsyncSpaceClient) -> object:
    return await space.get_blob((await space.list_blobs()).cids[0])


# every read of a repo, with the method that the last request of the read goes to
_REPO_READS = [
    pytest.param(_GET_RECORD, _get_record, id='get_record'),
    pytest.param(_GET_LATEST_COMMIT, _get_latest_commit, id='get_latest_commit'),
    pytest.param(_GET_REPO, _get_repo, id='get_repo'),
    pytest.param(_LIST_REPO_OPS, _list_repo_ops, id='list_repo_ops'),
    pytest.param(_LIST_RECORDS, _list_records, id='list_records'),
    pytest.param(_LIST_BLOBS, _list_blobs, id='list_blobs'),
    pytest.param(_GET_BLOB, _get_blob, id='get_blob'),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read'), _REPO_READS)
async def test_read_of_the_own_repo_asks_the_pds_of_the_account_for_no_mac(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    _put_note(network, BOB_DID, 'a')
    network.add_blob(SPACE, BOB_DID, _BLOB)
    request, sent = _recording_request(network)
    resolver = AsyncFakeIdResolver(network)
    space = await make_client(network, id_resolver=resolver, request=request)

    await read(space)

    asked = network.requests[-1]
    assert network.log[-1] == (BOB_PDS, nsid, 200)
    assert asked.url.params['repo'] == BOB_DID
    assert asked.headers['authorization'] == f'Bearer {network.accounts[BOB_DID].access_token}'
    assert 'accept-signature' not in asked.headers
    assert sent == []
    assert resolver.did.calls == []
    assert network.count(_AUTHORIZE) == 0


@pytest.mark.asyncio
async def test_own_repo_is_synced_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    request, sent = _recording_request(network)
    space = await make_client(network, request=request)
    await space.create_record(_note('kept'), 'kept')
    await space.create_record(_note('before'), 'updated')
    snapshot = await space.get_repo()
    index = {(record.collection, record.rkey): record.cid for record in snapshot.records}

    await space.put_record(_note('after'), 'updated')
    await space.create_record(_note('transient'), 'transient')
    await space.delete_record(_NOTE, 'transient')
    pulled = await space.pull_repo(snapshot.head, lambda collection, rkey: index.get((collection, rkey)))

    assert isinstance(pulled, RepoChanges)
    assert [(change.rkey, change.prev, change.value) for change in pulled.changes] == [
        ('updated', index[(_NOTE, 'updated')], _note('after'))
    ]
    assert pulled.head == (await space.get_repo()).head
    assert sent == []
    assert _origins(network) == {BOB_PDS}


@pytest.mark.asyncio
async def test_commit_of_the_own_repo_is_checked_without_a_mac(network: FakeSpaceNetwork) -> None:
    _put_note(network, BOB_DID, 'a')
    network.tamper_commit = lambda commit: commit.update(repo=ALICE_DID)
    space = await make_client(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification') as e:
        await space.get_latest_commit()

    assert str(e.value.__cause__) == f'Commit is for another repo: {ALICE_DID}'
    assert network.statuses(_GET_LATEST_COMMIT) == [200, 200]
    assert network.count(_AUTHORIZE) == 0


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L343-L357
@pytest.mark.asyncio
async def test_repo_of_another_account_is_read_from_its_pds_with_the_space_credential(
    network: FakeSpaceNetwork,
) -> None:
    cid = _put_note(network, ALICE_DID, 'a')
    request, sent = _recording_request(network)
    space = await make_client(network, request=request)

    record = await space.get_record(_NOTE, 'a', ALICE_DID)
    listed = await space.list_records(ALICE_DID, _NOTE)

    token_request, authorize, read, listing = network.requests
    credential = await space.authorize()
    assert (record.cid, record.value) == (cid, _note('hello'))
    assert [item.cid for item in listed.records] == [cid]
    assert network.log == [
        (BOB_PDS, _GET_DELEGATION_TOKEN, 200),
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (ALICE_PDS, _GET_RECORD, 200),
        (ALICE_PDS, _LIST_RECORDS, 200),
    ]
    assert sent == [authorize, read, listing]
    assert token_request.url.params['space'] == SPACE
    assert token_request.headers['authorization'] == f'Bearer {network.accounts[BOB_DID].access_token}'
    assert 'authorization' not in authorize.headers
    assert parse_space_token('delegation', json.loads(authorize.content)['delegationToken']).iss == BOB_DID
    for credentialed in (read, listing):
        assert credentialed.headers['authorization'] == f'Atproto-Space-Credential {credential.token}'
        assert credentialed.headers['atproto-space-audience'] == ALICE_DID
    assert 'accept-signature' in read.headers


async def _get_record_of_alice(space: AsyncSpaceClient) -> object:
    return await space.get_record(_NOTE, 'a', ALICE_DID)


async def _get_latest_commit_of_alice(space: AsyncSpaceClient) -> object:
    return await space.get_latest_commit(ALICE_DID)


async def _list_repo_ops_of_alice(space: AsyncSpaceClient) -> object:
    return await space.list_repo_ops(ALICE_DID)


async def _get_repo_of_alice(space: AsyncSpaceClient) -> object:
    return await space.get_repo(ALICE_DID)


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L385-L425
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('nsid', 'read'),
    [
        pytest.param(_GET_RECORD, _get_record_of_alice, id='get_record'),
        pytest.param(_GET_LATEST_COMMIT, _get_latest_commit_of_alice, id='get_latest_commit'),
        pytest.param(_LIST_REPO_OPS, _list_repo_ops_of_alice, id='list_repo_ops'),
        pytest.param(_GET_REPO, _get_repo_of_alice, id='get_repo'),
    ],
)
async def test_response_of_another_pds_without_a_mac_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.drop_mac = True
    space = await make_client(network)

    with pytest.raises(SpaceRepoVerificationError):
        await read(space)

    assert network.statuses(nsid) == [200, 200]


@pytest.mark.asyncio
async def test_credential_is_requested_anew_after_a_login_as_another_account(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    carol = network.add_account(_CAROL_DID, _CAROL_PDS)
    network.spaces[SPACE].members.add(_CAROL_DID)
    space = await make_client(network)
    bob_credential = await space.authorize()

    await space.client.logout_oauth()
    await space.client.login_oauth(FakeAuthSession(carol))
    assert (await space.get_record(_NOTE, 'a', ALICE_DID)).value == _note('hello')

    tokens = [json.loads(request.content)['delegationToken'] for request in network.requests_to(_AUTHORIZE)]
    assert [parse_space_token('delegation', token).iss for token in tokens] == [BOB_DID, _CAROL_DID]
    assert network.log == [
        (BOB_PDS, _GET_DELEGATION_TOKEN, 200),
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (_CAROL_PDS, _GET_DELEGATION_TOKEN, 200),
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (ALICE_PDS, _GET_RECORD, 200),
    ]
    assert await space.authorize() is not bob_credential
    assert network.count(_AUTHORIZE) == 2


@pytest.mark.asyncio
async def test_credential_of_an_account_does_not_admit_the_next_one(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    carol = network.add_account(_CAROL_DID, _CAROL_PDS)
    space = await make_client(network)
    await space.get_record(_NOTE, 'a', ALICE_DID)

    await space.client.logout_oauth()
    await space.client.login_oauth(FakeAuthSession(carol))

    # the second request finds no credential that the first one left behind
    for _ in range(2):
        with pytest.raises(BadRequestError, match='SpaceNotFound'):
            await space.get_record(_NOTE, 'a', ALICE_DID)

    assert network.statuses(_AUTHORIZE) == [200, 400, 400]
    assert network.statuses(_GET_RECORD) == [200]


@pytest.mark.asyncio
@pytest.mark.parametrize('login', [async_fake_client, async_fake_password_client], ids=['oauth', 'password'])
async def test_session_of_the_client_reaches_no_other_host_than_the_pds_of_the_account(
    network: FakeSpaceNetwork, login: _Login
) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.add_blob(SPACE, ALICE_DID, _BLOB)
    bob = network.accounts[BOB_DID]
    space = await make_client(network, login=login)
    network.requests.clear()

    await space.create_record(_note('a'), 'a')
    for repo in (None, ALICE_DID):
        await space.get_record(_NOTE, 'a', repo)
        await space.get_latest_commit(repo)
        await space.get_repo(repo)
        await space.list_repo_ops(repo)
        await space.list_records(repo)
        await space.list_blobs(repo)
    await space.get_blob((await space.list_blobs(ALICE_DID)).cids[0], ALICE_DID)
    assert len([record async for record in space.all_records()]) == 2

    bearer = f'Bearer {bob.access_token}'
    assert all(status == 200 for _, _, status in network.log)
    assert {request.url.host for request in network.requests} == {
        'bob.pds.test',
        'alice.pds.test',
        'authority.pds.test',
    }
    for request in network.requests:
        assert (request.headers.get('authorization') == bearer) == (request.url.host == 'bob.pds.test')


@pytest.mark.asyncio
async def test_all_records_reads_the_own_repo_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    request, sent = _recording_request(network)
    space = await make_client(network, space_type=_GROUP, request=request)
    await space.create_record(_note('b'), 'b')
    await space.create_record({'$type': _OTHER}, 'c')

    records = [record async for record in space.all_records()]

    assert [(record.repo, record.rkey, record.valid) for record in records] == [
        (ALICE_DID, 'a', True),
        (BOB_DID, 'b', True),
        (BOB_DID, 'c', False),
    ]
    assert sorted((request.url.host, request.url.path.rsplit('.', 1)[1]) for request in sent) == [
        ('alice.pds.test', 'getRepo'),
        ('authority.pds.test', 'authorizeSpaceSync'),
        ('authority.pds.test', 'listWriters'),
        ('authority.pds.test', 'listWriters'),
    ]
    assert sorted(network.log[-2:]) == [(ALICE_PDS, _GET_REPO, 200), (BOB_PDS, _GET_REPO, 200)]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L96-L111
@pytest.mark.asyncio
async def test_create_space_opens_the_space_that_the_pds_created(network: FakeSpaceNetwork) -> None:
    client = await async_fake_client(network, network.accounts[BOB_DID])
    request = AsyncRequest(transport=network.async_transport)

    created = await AsyncSpaceClient.create_space(
        client,
        _GROUP,
        models.ComAtprotoMemberspacePolicy.Main(),
        'created',
        id_resolver=async_fake_id_resolver(network),
        request=request,
    )
    await created.create_record(_note('first'))

    body = _body(network, _CREATE_SPACE)
    assert isinstance(created, AsyncSpaceClient)
    assert created.uri == f'at://{BOB_DID}/space/com.example.group/created'
    assert created.client is client
    assert created.space_type is _GROUP
    assert created.request is request
    assert (body['spaceType'], body['skey'], body['policy']['$type']) == (_GROUP.nsid, 'created', _MEMBERSPACE_POLICY)
    assert network.log[0] == (BOB_PDS, _CREATE_SPACE, 200)
    assert [record.value async for record in created.records(collection=_NOTE)] == [_note('first')]
    assert [writer.repo async for writer in created.writers()] == [BOB_DID]


@pytest.mark.asyncio
async def test_create_space_returns_a_client_of_the_space_in_the_response(network: FakeSpaceNetwork) -> None:
    client = await async_fake_client(network, network.accounts[BOB_DID])
    uri = f'at://{BOB_DID}/space/com.example.group/renamed'
    network.forced_responses[_CREATE_SPACE] = [httpx.Response(200, json={'space': uri})]

    created = await AsyncSpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main(), 'created')

    assert created.uri == uri


@pytest.mark.asyncio
async def test_create_space_validates_the_key_against_the_type(network: FakeSpaceNetwork) -> None:
    client = await async_fake_client(network, network.accounts[BOB_DID])
    policy = models.ComAtprotoPersonalspacePolicy.Main()

    with pytest.raises(ValueError, match=r'Key of a com\.example\.bookmarks space must be self'):
        await AsyncSpaceClient.create_space(client, _BOOKMARKS, policy, 'other')
    with pytest.raises(InvalidAtUriError, match='Space URI'):
        await AsyncSpaceClient.create_space(client, _GROUP, policy, 'a/b')
    assert network.requests == []

    literal = await AsyncSpaceClient.create_space(client, _BOOKMARKS, policy)
    generated = await AsyncSpaceClient.create_space(client, _GROUP, policy)
    untyped = await AsyncSpaceClient.create_space(client, 'com.example.bookmarks', policy, 'other')

    assert literal.ref == SpaceRef(BOB_DID, 'com.example.bookmarks', 'self')
    assert TID_RE.fullmatch(generated.ref.skey)
    assert (untyped.ref.skey, untyped.space_type) == ('other', None)
    assert [json.loads(request.content) for request in network.requests_to(_CREATE_SPACE)] == [
        {'spaceType': 'com.example.bookmarks', 'skey': 'self', 'policy': {'$type': _PERSONALSPACE_POLICY}},
        {'spaceType': 'com.example.group', 'policy': {'$type': _PERSONALSPACE_POLICY}},
        {'spaceType': 'com.example.bookmarks', 'skey': 'other', 'policy': {'$type': _PERSONALSPACE_POLICY}},
    ]


@pytest.mark.asyncio
async def test_create_space_requires_a_login(network: FakeSpaceNetwork) -> None:
    client = AsyncClient(request=AsyncRequest(transport=network.async_transport))

    with pytest.raises(LoginRequiredError):
        await AsyncSpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main())

    assert network.requests == []


@pytest.mark.asyncio
async def test_create_space_checks_the_request_before_it_creates_the_space(
    network: FakeSpaceNetwork,
) -> None:
    client = await async_fake_client(network, network.accounts[BOB_DID])
    policy = models.ComAtprotoPersonalspacePolicy.Main()

    with pytest.raises(ValueError, match='must carry no session of an account'):
        await AsyncSpaceClient.create_space(client, _BOOKMARKS, policy, request=client.request)

    assert network.count(_CREATE_SPACE) == 0
