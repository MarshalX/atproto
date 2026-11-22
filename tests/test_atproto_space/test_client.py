import json
import typing as t

import httpx
import pytest
from atproto_client import Client, models
from atproto_client.exceptions import BadRequestError, LoginRequiredError
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.string_formats import TID_RE
from atproto_client.request import Request
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_identity.cache.in_memory_cache import DidInMemoryCache
from atproto_space import RepoChanges, SpaceClient, SpaceReader, SpaceType
from atproto_space.exceptions import SpaceRepoVerificationError
from atproto_space.tokens import create_client_attestation, parse_space_token
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    ALICE_PDS,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    Account,
    FakeAuthSession,
    FakeIdResolver,
    FakeSpaceNetwork,
    build_network,
    fake_client,
    fake_id_resolver,
    fake_password_client,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_GET_DELEGATION_TOKEN = 'com.atproto.space.getDelegationToken'
_LIST_WRITERS = 'com.atproto.space.listWriters'
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
_POST = 'app.bsky.feed.post'
_OTHER = 'com.example.other'
_GROUP = SpaceType('com.example.group', 'any', (_NOTE, _POST))
_BOOKMARKS = SpaceType('com.example.bookmarks', 'literal:self')

_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'
_CAROL_PDS = 'https://carol.pds.test'

_CLIENT_ID = 'https://app.test/client-metadata.json'
_RKEY = '3jzfcijpj2z2a'
_CREATED_AT = '2026-11-20T00:00:00.000Z'
_BLOB = b'\x01\x02\x03\x04\x05'

_Login = t.Callable[[FakeSpaceNetwork, Account], Client]
_Read = t.Callable[[SpaceClient], object]
_Sent = t.List[httpx.Request]


def _recording_request(network: FakeSpaceNetwork) -> t.Tuple[Request, _Sent]:
    """Build an HTTP client of the network that keeps the requests that it sends."""
    sent: _Sent = []

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return network.handle(request)

    return Request(transport=httpx.MockTransport(handle)), sent


def make_client(
    network: FakeSpaceNetwork,
    did: str = BOB_DID,
    space_type: t.Optional[SpaceType] = None,
    login: _Login = fake_client,
    **kwargs: t.Any,
) -> SpaceClient:
    kwargs.setdefault('id_resolver', FakeIdResolver(network))
    kwargs.setdefault('request', Request(transport=network.transport))

    return SpaceClient(login(network, network.accounts[did]), SPACE, space_type, **kwargs)


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


def test_client_of_a_space_uri(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    space = SpaceClient(client, SPACE)

    assert isinstance(space, SpaceReader)
    assert space.client is client
    assert space.did == BOB_DID
    assert space.ref == SpaceRef(AUTHORITY_DID, 'com.example.group', 'main')
    assert space.uri == SPACE
    assert space.space_type is None
    assert space.request is not client.request
    assert isinstance(space._id_resolver.did._cache, DidInMemoryCache)


def test_client_of_a_space_ref(network: FakeSpaceNetwork) -> None:
    ref = SpaceRef.from_str(SPACE)
    request = Request()
    resolver = FakeIdResolver(network)

    space = make_client(network, space_type=_GROUP, id_resolver=resolver, request=request)

    assert space.ref == ref
    assert space.space_type is _GROUP
    assert space.request is request
    assert space._id_resolver is resolver


def test_client_refuses_a_space_of_another_type(network: FakeSpaceNetwork) -> None:
    with pytest.raises(ValueError, match=f'{SPACE} is not a com.example.bookmarks space'):
        make_client(network, space_type=_BOOKMARKS)


def test_client_requires_a_login() -> None:
    with pytest.raises(LoginRequiredError):
        SpaceClient(Client(), SPACE)


@pytest.mark.parametrize('login', [fake_client, fake_password_client], ids=['oauth', 'password'])
def test_client_refuses_the_request_of_a_client(network: FakeSpaceNetwork, login: _Login) -> None:
    client = login(network, network.accounts[BOB_DID])

    with pytest.raises(ValueError, match='must carry no session of an account'):
        SpaceClient(client, SPACE, request=client.request)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        SpaceClient(client, SPACE, request=client.request.clone())


@pytest.mark.parametrize('login', [fake_client, fake_password_client], ids=['oauth', 'password'])
def test_did_is_the_account_of_the_session(network: FakeSpaceNetwork, login: _Login) -> None:
    client = login(network, network.accounts[ALICE_DID])

    assert client.me is None
    assert SpaceClient(client, SPACE).did == ALICE_DID


def test_did_follows_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    space = make_client(network)

    space.client.login_oauth(FakeAuthSession(network.accounts[ALICE_DID]))
    assert space.did == ALICE_DID

    space.client.logout_oauth()
    with pytest.raises(LoginRequiredError):
        space.list_records()

    assert network.requests == []


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L185-L215
def test_own_repo_is_read_and_written_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    request, sent = _recording_request(network)
    resolver = FakeIdResolver(network)
    space = make_client(network, id_resolver=resolver, request=request)

    rkey = _rkey(space.create_record(_note('new')).uri)
    space.put_record(_note('updated'), rkey)
    assert space.get_record(_NOTE, rkey).value == _note('updated')

    space.apply_writes(
        [
            models.ComAtprotoSpaceApplyWrites.Delete(collection=_NOTE, rkey=rkey),
            models.ComAtprotoSpaceApplyWrites.Create(collection=_NOTE, value=DotDict(_note('batched'))),
        ]
    )
    assert [record.value for record in space.list_records(collection=_NOTE).records] == [_note('batched')]

    assert space.clear_records() is True
    assert list(space.records(collection=_NOTE)) == []

    assert sent == []
    assert resolver.did.calls == []
    assert network.count(_AUTHORIZE) == 0
    assert network.count(_GET_DELEGATION_TOKEN) == 0
    assert _origins(network) == {BOB_PDS}
    assert all(status == 200 for _, _, status in network.log)


def test_writes_name_the_space_the_repo_and_the_collection(network: FakeSpaceNetwork) -> None:
    space = make_client(network)

    created = space.create_record(_note('a'), 'a')
    generated = space.create_record(_note('b'), validate=False)
    replaced = space.put_record(_note('c'), 'a', validate=False)
    assert space.delete_record(_NOTE, 'a') is True
    results = space.apply_writes(
        [
            models.ComAtprotoSpaceApplyWrites.Update(
                collection=_NOTE, rkey=_rkey(generated.uri), value=DotDict(_note('d'))
            )
        ],
        validate=False,
    ).results
    assert space.clear_records() is True

    target = {'space': SPACE, 'repo': BOB_DID}
    assert created.uri == f'{SPACE}/{BOB_DID}/{_NOTE}/a'
    assert replaced.uri == created.uri
    assert replaced.cid != created.cid
    assert [result.py_type for result in results or []] == ['com.atproto.space.applyWrites#updateResult']
    assert [json.loads(request.content) for request in network.requests_to(_CREATE_RECORD)] == [
        {**target, 'collection': _NOTE, 'rkey': 'a', 'record': _note('a')},
        {**target, 'collection': _NOTE, 'validate': False, 'record': _note('b')},
    ]
    assert _body(network, _PUT_RECORD) == {
        **target,
        'collection': _NOTE,
        'rkey': 'a',
        'validate': False,
        'record': _note('c'),
    }
    assert _body(network, _DELETE_RECORD) == {**target, 'collection': _NOTE, 'rkey': 'a'}
    assert _body(network, _APPLY_WRITES) == {
        **target,
        'validate': False,
        'writes': [
            {
                '$type': 'com.atproto.space.applyWrites#update',
                'collection': _NOTE,
                'rkey': _rkey(generated.uri),
                'value': _note('d'),
            }
        ],
    }
    assert _body(network, _CLEAR_RECORDS) == target
    assert network.repos[(SPACE, BOB_DID)].records == {}


def test_record_model_is_written_to_the_collection_of_its_type(network: FakeSpaceNetwork) -> None:
    space = make_client(network)
    post = models.AppBskyFeedPost.Record(text='hello', created_at=_CREATED_AT)

    created = space.create_record(post)
    space.put_record(post, _RKEY)

    value = {'$type': _POST, 'text': 'hello', 'createdAt': _CREATED_AT}
    assert created.uri.startswith(f'{SPACE}/{BOB_DID}/{_POST}/')
    assert _body(network, _CREATE_RECORD)['collection'] == _POST
    assert _body(network, _CREATE_RECORD)['record'] == value
    assert _body(network, _PUT_RECORD)['collection'] == _POST
    assert [record.value for record in space.records()] == [post, post]


def test_record_without_a_type_is_not_written(network: FakeSpaceNetwork) -> None:
    space = make_client(network)

    with pytest.raises(ValueError, match='Record has no type'):
        space.create_record({'text': 'hello'})
    with pytest.raises(ValueError, match='Record has no type'):
        space.put_record(DotDict({'text': 'hello'}), _RKEY)

    assert network.requests == []


def test_write_of_a_collection_that_the_space_type_does_not_declare_is_left_to_the_pds(
    network: FakeSpaceNetwork,
) -> None:
    space = make_client(network, space_type=_GROUP)

    space.create_record({'$type': _OTHER}, 'a')

    record = next(iter(space.records()))
    assert (record.collection, record.valid) == (_OTHER, False)
    assert str(record.error) == f'{_OTHER} is not a collection of com.example.group spaces'


def _get_record(space: SpaceClient) -> object:
    return space.get_record(_NOTE, 'a')


def _get_latest_commit(space: SpaceClient) -> object:
    return space.get_latest_commit()


def _get_repo(space: SpaceClient) -> object:
    return space.get_repo()


def _list_repo_ops(space: SpaceClient) -> object:
    return space.list_repo_ops()


def _list_records(space: SpaceClient) -> object:
    return space.list_records()


def _list_blobs(space: SpaceClient) -> object:
    return space.list_blobs()


def _get_blob(space: SpaceClient) -> object:
    return space.get_blob(space.list_blobs().cids[0])


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


@pytest.mark.parametrize(('nsid', 'read'), _REPO_READS)
def test_read_of_the_own_repo_asks_the_pds_of_the_account_for_no_mac(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    _put_note(network, BOB_DID, 'a')
    network.add_blob(SPACE, BOB_DID, _BLOB)
    request, sent = _recording_request(network)
    resolver = FakeIdResolver(network)
    space = make_client(network, id_resolver=resolver, request=request)

    read(space)

    asked = network.requests[-1]
    assert network.log[-1] == (BOB_PDS, nsid, 200)
    assert asked.url.params['repo'] == BOB_DID
    assert asked.headers['authorization'] == f'Bearer {network.accounts[BOB_DID].access_token}'
    assert 'accept-signature' not in asked.headers
    assert sent == []
    assert resolver.did.calls == []
    assert network.count(_AUTHORIZE) == 0


def test_named_own_repo_is_read_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, BOB_DID, 'a')
    request, sent = _recording_request(network)
    space = make_client(network, request=request)

    assert space.get_record(_NOTE, 'a', BOB_DID).cid == cid
    assert [record.cid for record in space.records(BOB_DID)] == [cid]
    assert [record.cid for record in space.get_repo(BOB_DID).records] == [cid]

    assert sent == []
    assert _origins(network) == {BOB_PDS}


def test_own_repo_is_synced_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    request, sent = _recording_request(network)
    space = make_client(network, request=request)
    space.create_record(_note('kept'), 'kept')
    space.create_record(_note('before'), 'updated')
    snapshot = space.get_repo()
    index = {(record.collection, record.rkey): record.cid for record in snapshot.records}

    space.put_record(_note('after'), 'updated')
    space.create_record(_note('transient'), 'transient')
    space.delete_record(_NOTE, 'transient')
    pulled = space.pull_repo(snapshot.head, lambda collection, rkey: index.get((collection, rkey)))

    assert isinstance(pulled, RepoChanges)
    assert [(change.rkey, change.prev, change.value) for change in pulled.changes] == [
        ('updated', index[(_NOTE, 'updated')], _note('after'))
    ]
    assert pulled.head == space.get_repo().head
    assert sent == []
    assert _origins(network) == {BOB_PDS}


def test_own_record_is_taken_as_the_pds_of_the_account_returns_it(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, BOB_DID, 'a')
    uri = f'{SPACE}/{BOB_DID}/{_NOTE}/other'
    network.forced_responses[_GET_RECORD] = [httpx.Response(200, json={'uri': uri, 'cid': cid, 'value': _note('x')})]
    space = make_client(network)

    record = space.get_record(_NOTE, 'a')

    assert (record.uri, record.cid, record.value) == (uri, cid, _note('x'))
    assert network.count(_GET_RECORD) == 1


@pytest.mark.parametrize(
    ('nsid', 'read', 'message'),
    [
        pytest.param(_GET_LATEST_COMMIT, _get_latest_commit, 'commit failed verification', id='get_latest_commit'),
        pytest.param(_GET_REPO, _get_repo, 'failed verification', id='get_repo'),
        pytest.param(_LIST_REPO_OPS, _list_repo_ops, 'commit failed verification', id='list_repo_ops'),
    ],
)
def test_commit_of_the_own_repo_is_checked_without_a_mac(
    network: FakeSpaceNetwork, nsid: str, read: _Read, message: str
) -> None:
    _put_note(network, BOB_DID, 'a')
    network.tamper_commit = lambda commit: commit.update(repo=ALICE_DID)
    space = make_client(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} {message}') as e:
        read(space)

    assert str(e.value.__cause__) == f'Commit is for another repo: {ALICE_DID}'
    assert network.statuses(nsid) == [200, 200]
    assert network.count(_AUTHORIZE) == 0


def test_records_of_the_own_repo_are_checked_against_its_commit(network: FakeSpaceNetwork) -> None:
    _put_note(network, BOB_DID, 'a')
    network.tamper_archive = lambda pairs: pairs.clear()
    space = make_client(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} failed verification'):
        space.get_repo()


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L343-L357
def test_repo_of_another_account_is_read_from_its_pds_with_the_space_credential(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, ALICE_DID, 'a')
    request, sent = _recording_request(network)
    space = make_client(network, request=request)

    record = space.get_record(_NOTE, 'a', ALICE_DID)
    listed = space.list_records(ALICE_DID, _NOTE)

    token_request, authorize, read, listing = network.requests
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
        assert credentialed.headers['authorization'] == f'Atproto-Space-Credential {space.authorize().token}'
        assert credentialed.headers['atproto-space-audience'] == ALICE_DID
    assert 'accept-signature' in read.headers


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L359-L370
def test_writers_are_listed_from_the_host_of_the_space(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    space = make_client(network)
    space.create_record(_note('b'))

    writers = list(space.writers())

    listing = network.requests_to(_LIST_WRITERS)[0]
    assert [(writer.py_type, writer.repo) for writer in writers] == [
        ('com.atproto.space.defs#repoWrite', ALICE_DID),
        ('com.atproto.space.defs#repoWrite', BOB_DID),
    ]
    assert network.statuses(_LIST_WRITERS) == [200, 200]
    assert listing.url.host == httpx.URL(AUTHORITY_PDS).host
    assert listing.headers['atproto-space-audience'] == AUTHORITY_DID


def test_every_credential_is_requested_with_a_delegation_token_of_its_own(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    space = make_client(network)

    space.authorize()
    space.list_records(ALICE_DID)
    network.revoke_credentials()
    space.list_records(ALICE_DID)

    tokens = [json.loads(request.content)['delegationToken'] for request in network.requests_to(_AUTHORIZE)]
    assert network.statuses(_GET_DELEGATION_TOKEN) == [200, 200]
    assert network.statuses(_LIST_RECORDS) == [200, 401, 200]
    assert len(set(tokens)) == 2


def test_credential_is_requested_with_the_client_attestation_and_the_notify_registration(
    network: FakeSpaceNetwork,
) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())

    def provide_client_attestation(audience: str) -> str:
        return create_client_attestation(_CLIENT_ID, audience, private_key)

    def provide_notify_registration(_: SpaceRef) -> 'models.ComAtprotoSpaceAuthorizeSpaceSync.Notify':
        return models.ComAtprotoSpaceAuthorizeSpaceSync.Notify(endpoint='https://syncer.example', token='secret')

    space = make_client(
        network,
        client_attestation_provider=provide_client_attestation,
        notify_registration_provider=provide_notify_registration,
    )

    space.authorize()

    body = _body(network, _AUTHORIZE)
    assert set(body) == {'space', 'credentialKey', 'delegationToken', 'clientAttestation', 'notify'}
    assert parse_space_token('client_attestation', body['clientAttestation']).aud == f'{AUTHORITY_DID}#atproto_pds'
    assert (body['notify']['endpoint'], body['notify']['token']) == ('https://syncer.example', 'secret')


def _get_record_of_alice(space: SpaceClient) -> object:
    return space.get_record(_NOTE, 'a', ALICE_DID)


def _get_latest_commit_of_alice(space: SpaceClient) -> object:
    return space.get_latest_commit(ALICE_DID)


def _list_repo_ops_of_alice(space: SpaceClient) -> object:
    return space.list_repo_ops(ALICE_DID)


def _get_repo_of_alice(space: SpaceClient) -> object:
    return space.get_repo(ALICE_DID)


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L385-L425
@pytest.mark.parametrize(
    ('nsid', 'read'),
    [
        pytest.param(_GET_RECORD, _get_record_of_alice, id='get_record'),
        pytest.param(_GET_LATEST_COMMIT, _get_latest_commit_of_alice, id='get_latest_commit'),
        pytest.param(_LIST_REPO_OPS, _list_repo_ops_of_alice, id='list_repo_ops'),
        pytest.param(_GET_REPO, _get_repo_of_alice, id='get_repo'),
    ],
)
def test_response_of_another_pds_without_a_mac_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.drop_mac = True
    space = make_client(network)

    with pytest.raises(SpaceRepoVerificationError):
        read(space)

    assert network.statuses(nsid) == [200, 200]


def test_space_that_does_not_admit_the_account(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].members.discard(BOB_DID)
    space = make_client(network)

    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        space.list_writers()
    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        space.list_records(ALICE_DID)

    assert space.list_records().records == []
    assert network.statuses(_AUTHORIZE) == [400, 400]


def test_credential_is_requested_anew_after_a_login_as_another_account(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    carol = network.add_account(_CAROL_DID, _CAROL_PDS)
    network.spaces[SPACE].members.add(_CAROL_DID)
    space = make_client(network)
    bob_credential = space.authorize()

    space.client.logout_oauth()
    space.client.login_oauth(FakeAuthSession(carol))
    assert space.get_record(_NOTE, 'a', ALICE_DID).value == _note('hello')

    tokens = [json.loads(request.content)['delegationToken'] for request in network.requests_to(_AUTHORIZE)]
    assert [parse_space_token('delegation', token).iss for token in tokens] == [BOB_DID, _CAROL_DID]
    assert network.log == [
        (BOB_PDS, _GET_DELEGATION_TOKEN, 200),
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (_CAROL_PDS, _GET_DELEGATION_TOKEN, 200),
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (ALICE_PDS, _GET_RECORD, 200),
    ]
    assert space.authorize() is not bob_credential
    assert network.count(_AUTHORIZE) == 2


def test_credential_of_an_account_does_not_admit_the_next_one(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    carol = network.add_account(_CAROL_DID, _CAROL_PDS)
    space = make_client(network)
    space.get_record(_NOTE, 'a', ALICE_DID)

    space.client.logout_oauth()
    space.client.login_oauth(FakeAuthSession(carol))

    # the second request finds no credential that the first one left behind
    for _ in range(2):
        with pytest.raises(BadRequestError, match='SpaceNotFound'):
            space.get_record(_NOTE, 'a', ALICE_DID)

    assert network.statuses(_AUTHORIZE) == [200, 400, 400]
    assert network.statuses(_GET_RECORD) == [200]


@pytest.mark.parametrize('login', [fake_client, fake_password_client], ids=['oauth', 'password'])
def test_session_of_the_client_reaches_no_other_host_than_the_pds_of_the_account(
    network: FakeSpaceNetwork, login: _Login
) -> None:
    _put_note(network, ALICE_DID, 'a')
    network.add_blob(SPACE, ALICE_DID, _BLOB)
    bob = network.accounts[BOB_DID]
    space = make_client(network, login=login)
    network.requests.clear()

    space.create_record(_note('a'), 'a')
    for repo in (None, ALICE_DID):
        space.get_record(_NOTE, 'a', repo)
        space.get_latest_commit(repo)
        space.get_repo(repo)
        space.list_repo_ops(repo)
        space.list_records(repo)
        space.list_blobs(repo)
    space.get_blob(space.list_blobs(ALICE_DID).cids[0], ALICE_DID)
    assert len(list(space.all_records())) == 2

    bearer = f'Bearer {bob.access_token}'
    assert all(status == 200 for _, _, status in network.log)
    assert {request.url.host for request in network.requests} == {
        'bob.pds.test',
        'alice.pds.test',
        'authority.pds.test',
    }
    for request in network.requests:
        assert (request.headers.get('authorization') == bearer) == (request.url.host == 'bob.pds.test')


def test_all_records_reads_the_own_repo_with_the_session_of_the_client(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    request, sent = _recording_request(network)
    space = make_client(network, space_type=_GROUP, request=request)
    space.create_record(_note('b'), 'b')
    space.create_record({'$type': _OTHER}, 'c')

    records = list(space.all_records())

    assert [(record.repo, record.rkey, record.valid) for record in records] == [
        (ALICE_DID, 'a', True),
        (BOB_DID, 'b', True),
        (BOB_DID, 'c', False),
    ]
    assert [(request.url.host, request.url.path.rsplit('.', 1)[1]) for request in sent] == [
        ('authority.pds.test', 'authorizeSpaceSync'),
        ('authority.pds.test', 'listWriters'),
        ('authority.pds.test', 'listWriters'),
        ('alice.pds.test', 'getRepo'),
    ]
    assert network.log[-2:] == [(ALICE_PDS, _GET_REPO, 200), (BOB_PDS, _GET_REPO, 200)]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L96-L111
def test_create_space_opens_the_space_that_the_pds_created(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])
    request = Request(transport=network.transport)

    created = SpaceClient.create_space(
        client,
        _GROUP,
        models.ComAtprotoMemberspacePolicy.Main(),
        'created',
        id_resolver=fake_id_resolver(network),
        request=request,
    )
    created.create_record(_note('first'))

    body = _body(network, _CREATE_SPACE)
    assert isinstance(created, SpaceClient)
    assert created.uri == f'at://{BOB_DID}/space/com.example.group/created'
    assert created.client is client
    assert created.space_type is _GROUP
    assert created.request is request
    assert (body['spaceType'], body['skey'], body['policy']['$type']) == (_GROUP.nsid, 'created', _MEMBERSPACE_POLICY)
    assert network.log[0] == (BOB_PDS, _CREATE_SPACE, 200)
    assert [record.value for record in created.list_records(collection=_NOTE).records] == [_note('first')]
    assert [writer.repo for writer in created.writers()] == [BOB_DID]


def test_create_space_returns_a_client_of_the_space_in_the_response(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])
    uri = f'at://{BOB_DID}/space/com.example.group/renamed'
    network.forced_responses[_CREATE_SPACE] = [httpx.Response(200, json={'space': uri})]

    created = SpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main(), 'created')

    assert created.uri == uri


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L113-L118
def test_create_space_defaults_the_key_of_a_literal_key_type(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    created = SpaceClient.create_space(client, _BOOKMARKS, models.ComAtprotoPersonalspacePolicy.Main())
    same = SpaceClient.create_space(
        fake_client(network, network.accounts[ALICE_DID]), _BOOKMARKS, DotDict({'$type': _PERSONALSPACE_POLICY}), 'self'
    )

    assert created.ref == SpaceRef(BOB_DID, 'com.example.bookmarks', 'self')
    assert same.ref == SpaceRef(ALICE_DID, 'com.example.bookmarks', 'self')
    assert [json.loads(request.content) for request in network.requests_to(_CREATE_SPACE)] == [
        {'spaceType': _BOOKMARKS.nsid, 'skey': 'self', 'policy': {'$type': _PERSONALSPACE_POLICY}}
    ] * 2
    assert network.spaces[created.uri].policy == {'$type': _PERSONALSPACE_POLICY}


def test_create_space_refuses_another_key_than_the_literal_one(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    with pytest.raises(ValueError, match=r'Key of a com\.example\.bookmarks space must be self'):
        SpaceClient.create_space(client, _BOOKMARKS, models.ComAtprotoPersonalspacePolicy.Main(), 'other')

    assert network.requests == []


def test_create_space_refuses_a_key_that_is_not_a_record_key(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    with pytest.raises(InvalidAtUriError, match='Space URI'):
        SpaceClient.create_space(client, _GROUP, models.ComAtprotoPersonalspacePolicy.Main(), 'a/b')

    assert network.requests == []


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L120-L125
def test_create_space_lets_the_pds_generate_any_other_key(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])

    created = SpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main())

    assert 'skey' not in _body(network, _CREATE_SPACE)
    assert TID_RE.fullmatch(created.ref.skey)
    assert created.ref.space_did == BOB_DID


def test_create_space_of_the_nsid_of_a_type(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])
    policy = models.ComAtprotoManagedspacePolicy.Main(managing_app='did:web:app.example#forum')

    created = SpaceClient.create_space(client, 'com.example.bookmarks', policy, 'other')
    generated = SpaceClient.create_space(client, 'com.example.bookmarks', policy)

    assert created.uri == f'at://{BOB_DID}/space/com.example.bookmarks/other'
    assert created.space_type is None
    assert TID_RE.fullmatch(generated.ref.skey)
    assert network.spaces[created.uri].policy == {
        '$type': 'com.atproto.managedspace.policy',
        'managingApp': 'did:web:app.example#forum',
        'publishPolicy': False,
    }


def test_create_space_that_exists(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[AUTHORITY_DID])

    with pytest.raises(BadRequestError, match='SpaceAlreadyExists'):
        SpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main(), 'main')


def test_create_space_requires_a_login(network: FakeSpaceNetwork) -> None:
    client = Client(request=Request(transport=network.transport))

    with pytest.raises(LoginRequiredError):
        SpaceClient.create_space(client, _GROUP, models.ComAtprotoMemberspacePolicy.Main())

    assert network.requests == []


def test_create_space_checks_the_request_before_it_creates_the_space(network: FakeSpaceNetwork) -> None:
    client = fake_client(network, network.accounts[BOB_DID])
    policy = models.ComAtprotoPersonalspacePolicy.Main()

    with pytest.raises(ValueError, match='must carry no session of an account'):
        SpaceClient.create_space(client, _BOOKMARKS, policy, request=client.request)

    assert network.count(_CREATE_SPACE) == 0
