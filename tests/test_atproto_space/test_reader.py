import json
import threading
import time
import typing as t

import httpx
import pytest
from atproto_client import Client, models
from atproto_client.exceptions import (
    BadRequestError,
    ModelError,
    NetworkError,
    RequestException,
    UnauthorizedError,
)
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.utils import get_response_model
from atproto_client.request import Request
from atproto_core._effects import run_flow
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_identity.cache.in_memory_cache import DidInMemoryCache
from atproto_identity.exceptions import DidNotFoundError
from atproto_space import SpaceReader, SpaceType
from atproto_space.exceptions import SpaceIdentityError
from atproto_space.mac import COMMIT_MAC_PROFILE, verify_commit_mac
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
    FakeIdResolver,
    FakeSpaceNetwork,
    build_network,
    delegation_token_provider,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_LIST_WRITERS = 'com.atproto.space.listWriters'
_LIST_RECORDS = 'com.atproto.space.listRecords'
_LIST_BLOBS = 'com.atproto.space.listBlobs'
_GET_LATEST_COMMIT = 'com.atproto.space.getLatestCommit'

_REPO_WRITE = 'com.atproto.space.defs#repoWrite'
_REPO_REMOVED = 'com.atproto.space.defs#repoRemoved'

_NOTE = 'com.example.note'
_POST = 'app.bsky.feed.post'
_BLOCK = 'app.bsky.graph.block'
_OTHER = 'com.example.other'
_GROUP = SpaceType('com.example.group', 'any', (_POST, _BLOCK))

_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'
_CAROL_PDS = 'https://carol.pds.test'
_UNKNOWN_DID = 'did:plc:unknownunknownunknownunk'
# the directory of the test suite does not know it
_UNKNOWN_PLC_DID = 'did:plc:kvwvcn5iqfooopmyzvb41234'
_CLIENT_ID = 'https://app.test/client-metadata.json'

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/src/space-reader.test.ts
_REV = '3jzfcijpj2z2a'
_CID = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'
_CREATED_AT = '2026-11-20T00:00:00.000Z'
_POST_VALUE = {'$type': _POST, 'text': 'hello', 'createdAt': _CREATED_AT}
_BLOCK_VALUE = {'$type': _BLOCK, 'subject': BOB_DID, 'createdAt': _CREATED_AT}

_CONCURRENCY = 8


def make_reader(network: FakeSpaceNetwork, space_type: t.Optional[SpaceType] = None, **kwargs: t.Any) -> SpaceReader:
    kwargs.setdefault('delegation_token_provider', delegation_token_provider(network, ALICE_DID))
    kwargs.setdefault('id_resolver', FakeIdResolver(network))
    kwargs.setdefault('request', Request(transport=network.transport))

    return SpaceReader(SPACE, space_type, **kwargs)


@pytest.fixture
def network() -> FakeSpaceNetwork:
    return build_network()


def _put_note(network: FakeSpaceNetwork, repo: str, rkey: str) -> str:
    return network.put_record(SPACE, repo, _NOTE, rkey, {'$type': _NOTE, 'text': 'hello'})


def _reply(body: t.Dict[str, t.Any]) -> httpx.Response:
    return httpx.Response(200, json=body)


def _reject() -> httpx.Response:
    return httpx.Response(401, json={'error': 'AuthenticationRequired', 'message': 'Revoked'})


def _write(repo: str) -> t.Dict[str, t.Any]:
    return {'$type': _REPO_WRITE, 'repo': repo, 'repoRev': _REV, 'data': {'$bytes': 'AAAA'}, 'spaceRev': _REV}


def _listed(rkey: str, collection: str, value: t.Optional[t.Dict[str, t.Any]] = None) -> t.Dict[str, t.Any]:
    listed: t.Dict[str, t.Any] = {'collection': collection, 'rkey': rkey, 'cid': _CID}
    if value is not None:
        listed['value'] = value

    return listed


def _record(rkey: str) -> t.Dict[str, t.Any]:
    return _listed(rkey, _NOTE, {'$type': _NOTE})


# one record for each way a listed record is classified
_CLASSIFIED = [
    _listed('valid', _POST, _POST_VALUE),
    _listed('invalid', _POST, {'$type': _POST}),
    _listed('task', _BLOCK, _BLOCK_VALUE),
    _listed('undeclared', _OTHER, {'$type': _OTHER}),
    _listed('mislisted', _POST, _BLOCK_VALUE),
    _listed('untyped', _POST, {'text': 'hello'}),
    _listed('excluded', _POST),
]


def _cursors(network: FakeSpaceNetwork, nsid: str) -> t.List[t.Optional[str]]:
    return [request.url.params.get('cursor') for request in network.requests_to(nsid)]


def _bodies(network: FakeSpaceNetwork, nsid: str) -> t.List[t.Dict[str, t.Any]]:
    return [json.loads(request.content) for request in network.requests_to(nsid)]


def _present(reader: SpaceReader) -> str:
    return f'Atproto-Space-Credential {reader.authorize().token}'


def _run_in_threads(target: t.Callable[[], object]) -> t.List[BaseException]:
    errors: t.List[BaseException] = []

    def worker() -> None:
        try:
            target()
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(_CONCURRENCY)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return errors


def test_reader_of_a_space_uri() -> None:
    reader = SpaceReader(SPACE)

    assert reader.ref == SpaceRef(AUTHORITY_DID, 'com.example.group', 'main')
    assert reader.uri == SPACE
    assert reader.space_type is None
    assert isinstance(reader.request, Request)
    assert isinstance(reader._id_resolver.did._cache, DidInMemoryCache)


def test_reader_of_a_space_ref() -> None:
    ref = SpaceRef.from_str(SPACE)
    request = Request()

    reader = SpaceReader(ref, _GROUP, request=request)

    assert reader.ref is ref
    assert reader.uri == SPACE
    assert reader.space_type is _GROUP
    assert reader.request is request


def test_reader_refuses_a_space_of_another_type() -> None:
    with pytest.raises(ValueError, match=f'{SPACE} is not a com.example.forum space'):
        SpaceReader(SPACE, SpaceType('com.example.forum', 'any'))


def test_reader_refuses_a_request_that_carries_a_session() -> None:
    request = Request()
    request.add_additional_header('authorization', 'Bearer token')

    with pytest.raises(ValueError, match='must carry no session of an account'):
        SpaceReader(SPACE, request=request)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        SpaceReader(SPACE, request=Client().request)


def test_reader_refuses_a_request_that_a_client_was_given_since(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    reader.authorize()
    Client(request=reader.request)
    network.requests.clear()

    with pytest.raises(ValueError, match='must carry no session of an account'):
        reader.list_records(BOB_DID)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        reader.authorize(renew=True)

    assert network.requests == []


@pytest.mark.parametrize(
    'space',
    [
        f'{SPACE}/{ALICE_DID}/{_NOTE}/a',
        'at://alice.test/space/com.example.group/main',
        f'at://{AUTHORITY_DID}/com.example.group/main',
    ],
)
def test_reader_refuses_a_uri_that_is_not_a_space_reference(space: str) -> None:
    with pytest.raises(InvalidAtUriError):
        SpaceReader(space)


def test_credential_request(network: FakeSpaceNetwork) -> None:
    refs: t.List[SpaceRef] = []

    def provide_delegation_token(ref: SpaceRef) -> str:
        refs.append(ref)
        return network.create_delegation_token(ALICE_DID, str(ref))

    reader = make_reader(network, delegation_token_provider=provide_delegation_token)

    credential = reader.authorize()

    request = network.requests_to(_AUTHORIZE)[0]
    body = json.loads(request.content)
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200)]
    assert request.headers['content-type'] == 'application/json'
    assert 'authorization' not in request.headers
    assert set(body) == {'space', 'credentialKey', 'delegationToken'}
    assert body['space'] == SPACE
    assert parse_space_token('delegation', body['delegationToken']).iss == ALICE_DID
    assert parse_space_token('credential', credential.token).key_id == body['credentialKey']
    assert refs == [reader.ref]


def test_reads_share_one_credential(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    for _ in range(5):
        reader.list_writers()
        reader.list_records(ALICE_DID)
        reader.list_records(BOB_DID)
        reader.list_blobs(BOB_DID)

    reads = network.requests[1:]
    assert network.count(_AUTHORIZE) == 1
    assert len(reads) == 20
    assert {request.headers['authorization'] for request in reads} == {_present(reader)}


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L652-L663
def test_authorize_returns_the_credential_until_it_is_renewed(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    reader = make_reader(network)

    credential = reader.authorize()
    assert credential.space_rev == network.spaces[SPACE].writers[ALICE_DID].space_rev
    assert reader.authorize() is credential

    renewed = reader.authorize(renew=True)
    assert renewed.token != credential.token
    assert reader.authorize() is renewed
    assert network.count(_AUTHORIZE) == 2


def test_every_credential_is_bound_to_a_key_of_its_own(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    reader.authorize()
    reader.authorize(renew=True)

    first, second = _bodies(network, _AUTHORIZE)
    assert first['credentialKey'] != second['credentialKey']
    assert first['delegationToken'] != second['delegationToken']


def test_rejected_credential_is_renewed_and_the_request_retried(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    reader = make_reader(network)
    reader.authorize()
    network.revoke_credentials()

    assert [writer.repo for writer in reader.list_writers().repos] == [ALICE_DID]

    rejected, retried = network.requests_to(_LIST_WRITERS)
    assert network.count(_AUTHORIZE) == 2
    assert network.statuses(_LIST_WRITERS) == [401, 200]
    assert retried.headers['authorization'] == _present(reader)
    assert rejected.headers['authorization'] != retried.headers['authorization']


def test_rejected_credential_is_renewed_only_once(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [_reject(), _reject()]
    reader = make_reader(network)

    with pytest.raises(UnauthorizedError, match='401 AuthenticationRequired'):
        reader.list_writers()

    assert network.count(_AUTHORIZE) == 2
    assert network.count(_LIST_WRITERS) == 2


def test_forbidden_request_is_not_retried(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [httpx.Response(403, json={'error': 'Forbidden', 'message': 'Forbidden'})]
    reader = make_reader(network)

    with pytest.raises(UnauthorizedError, match='403 Forbidden'):
        reader.list_writers()

    assert network.count(_AUTHORIZE) == 1
    assert network.count(_LIST_WRITERS) == 1


def test_host_that_redirects_in_a_loop_is_a_network_error(network: FakeSpaceNetwork) -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(_LIST_RECORDS):
            return httpx.Response(302, headers={'location': str(request.url)})

        return network.handle(request)

    reader = make_reader(network, request=Request(transport=httpx.MockTransport(handle)))

    with pytest.raises(NetworkError):
        reader.list_records(BOB_DID)

    assert network.count(_AUTHORIZE) == 1


@pytest.mark.parametrize('did', [AUTHORITY_DID, BOB_DID], ids=['space authority', 'repo'])
def test_host_with_a_malformed_pds_endpoint_is_a_network_error(network: FakeSpaceNetwork, did: str) -> None:
    network.accounts[did].pds = 'https://pds.test:8a'
    reader = make_reader(network)

    with pytest.raises(NetworkError):
        reader.list_records(BOB_DID)

    assert network.count(_LIST_RECORDS) == 0


def test_renewal_resolves_the_space_authority_again(network: FakeSpaceNetwork) -> None:
    resolver = FakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)
    reader.authorize()
    resolver.did.calls.clear()

    reader.authorize(renew=True)

    assert resolver.did.calls == [(AUTHORITY_DID, True)]


def test_retry_resolves_the_audience_and_the_space_authority_again(network: FakeSpaceNetwork) -> None:
    resolver = FakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)
    reader.authorize()
    network.revoke_credentials()
    resolver.did.calls.clear()

    reader.list_records(BOB_DID)

    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, True), (AUTHORITY_DID, True)]


def test_credential_is_renewed_before_it_expires(network: FakeSpaceNetwork, monkeypatch: pytest.MonkeyPatch) -> None:
    resolver = FakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)
    credential = reader.authorize()
    resolver.did.calls.clear()
    monkeypatch.setattr(time, 'time', lambda: credential.renew_at)

    reader.list_writers()

    assert network.count(_AUTHORIZE) == 2
    assert network.requests_to(_LIST_WRITERS)[0].headers['authorization'] == _present(reader)
    assert reader.authorize() is not credential
    assert resolver.did.calls == [(AUTHORITY_DID, False), (AUTHORITY_DID, False)]


def test_credential_of_a_deleted_space_is_dropped(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    reader.authorize()
    network.spaces[SPACE].deleted = True

    with pytest.raises(BadRequestError, match='SpaceDeleted'):
        reader.authorize(renew=True)

    network.spaces[SPACE].deleted = False
    reader.authorize()

    assert network.count(_AUTHORIZE) == 3


def test_credential_of_a_space_that_is_deleted_without_a_message_is_dropped(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    reader.authorize()
    network.forced_responses[_AUTHORIZE] = [httpx.Response(400, json={'error': 'SpaceDeleted'})]

    with pytest.raises(BadRequestError, match='SpaceDeleted'):
        reader.authorize(renew=True)

    reader.authorize()

    assert network.count(_AUTHORIZE) == 3


def test_credential_is_kept_when_its_renewal_fails(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    credential = reader.authorize()
    network.forced_responses[_AUTHORIZE] = [
        httpx.Response(500, json={'error': 'InternalServerError', 'message': 'Internal Server Error'})
    ]

    with pytest.raises(RequestException, match='InternalServerError'):
        reader.authorize(renew=True)

    assert reader.authorize() is credential
    assert network.count(_AUTHORIZE) == 2


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L665-L676
def test_refused_credential_request_is_not_remembered(network: FakeSpaceNetwork) -> None:
    network.add_account(_CAROL_DID, _CAROL_PDS)
    reader = make_reader(network, delegation_token_provider=delegation_token_provider(network, _CAROL_DID))

    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        reader.authorize()
    with pytest.raises(BadRequestError, match='SpaceNotFound'):
        reader.list_writers()

    assert network.count(_AUTHORIZE) == 2
    assert network.count(_LIST_WRITERS) == 0

    network.spaces[SPACE].members.add(_CAROL_DID)

    assert reader.list_writers().repos == []
    assert network.count(_AUTHORIZE) == 3


def test_notify_registration_is_sent_with_every_credential_request(network: FakeSpaceNetwork) -> None:
    notify = models.ComAtprotoSpaceAuthorizeSpaceSync.Notify(endpoint='https://syncer.example', token='secret')
    refs: t.List[SpaceRef] = []

    def provide_notify_registration(ref: SpaceRef) -> 'models.ComAtprotoSpaceAuthorizeSpaceSync.Notify':
        refs.append(ref)
        return notify

    reader = make_reader(network, notify_registration_provider=provide_notify_registration)

    reader.authorize()
    reader.authorize(renew=True)

    registrations = [body['notify'] for body in _bodies(network, _AUTHORIZE)]
    assert [(registration['endpoint'], registration['token']) for registration in registrations] == [
        ('https://syncer.example', 'secret'),
        ('https://syncer.example', 'secret'),
    ]
    assert refs == [reader.ref, reader.ref]


def test_client_attestation_is_requested_for_the_host_of_the_space(network: FakeSpaceNetwork) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    audiences: t.List[str] = []

    def provide_client_attestation(audience: str) -> str:
        audiences.append(audience)
        return create_client_attestation(_CLIENT_ID, audience, private_key)

    reader = make_reader(network, client_attestation_provider=provide_client_attestation)

    reader.authorize()

    client_attestation = _bodies(network, _AUTHORIZE)[0]['clientAttestation']
    assert audiences == [f'{AUTHORITY_DID}#atproto_pds']
    assert parse_space_token('client_attestation', client_attestation).iss == _CLIENT_ID


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L692-L708
def test_public_space_is_read_without_a_delegation_token(network: FakeSpaceNetwork) -> None:
    network.spaces[SPACE].public = True
    _put_note(network, ALICE_DID, 'a')
    reader = make_reader(network, delegation_token_provider=None)

    records = reader.list_records(ALICE_DID).records

    assert [record.rkey for record in records] == ['a']
    assert set(_bodies(network, _AUTHORIZE)[0]) == {'space', 'credentialKey'}


def test_space_authority_without_a_pds(network: FakeSpaceNetwork) -> None:
    network.accounts[AUTHORITY_DID].pds = ''
    reader = make_reader(network)

    with pytest.raises(SpaceIdentityError, match=f'DID document of {AUTHORITY_DID} has no PDS endpoint'):
        reader.authorize()

    assert network.requests == []


def test_audience_without_a_pds_costs_no_credential(network: FakeSpaceNetwork) -> None:
    network.add_account(_CAROL_DID, '')
    reader = make_reader(network)

    with pytest.raises(SpaceIdentityError, match=f'DID document of {_CAROL_DID} has no PDS endpoint'):
        reader.list_records(_CAROL_DID)

    assert network.requests == []


def test_unknown_audience_costs_no_credential(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(DidNotFoundError):
        reader.list_records(_UNKNOWN_DID)

    assert network.requests == []


def test_unknown_audience_is_not_found_by_the_default_resolver(network: FakeSpaceNetwork) -> None:
    reader = SpaceReader(SPACE, request=Request(transport=network.transport))

    with pytest.raises(DidNotFoundError):
        reader.list_records(_UNKNOWN_PLC_DID)

    assert network.requests == []


def test_list_writers_asks_the_host_of_the_space(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'b')
    network.remove_writer(SPACE, ALICE_DID)
    reader = make_reader(network)

    response = reader.list_writers()

    request = network.requests_to(_LIST_WRITERS)[0]
    assert [(type(writer), writer.repo) for writer in response.repos] == [
        (models.ComAtprotoSpaceDefs.RepoWrite, BOB_DID),
        (models.ComAtprotoSpaceDefs.RepoRemoved, ALICE_DID),
    ]
    assert response.cursor == network.spaces[SPACE].writers[ALICE_DID].space_rev
    assert network.log[-1] == (AUTHORITY_PDS, _LIST_WRITERS, 200)
    assert dict(request.url.params) == {'space': SPACE}
    assert request.headers['atproto-space-audience'] == AUTHORITY_DID
    assert 'accept-signature' not in request.headers


def test_list_writers_passes_the_limit_and_the_cursor(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    first = reader.list_writers(limit=1)
    second = reader.list_writers(limit=1, cursor=first.cursor)

    assert [writer.repo for writer in first.repos] == [ALICE_DID]
    assert [writer.repo for writer in second.repos] == [BOB_DID]


def test_list_records_asks_the_pds_of_the_repo(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    response = reader.list_records(BOB_DID)

    request = network.requests_to(_LIST_RECORDS)[0]
    assert [(record.collection, record.rkey, record.cid) for record in response.records] == [(_NOTE, 'b', cid)]
    assert response.records[0].value == {'$type': _NOTE, 'text': 'hello'}
    assert network.log[-1] == (BOB_PDS, _LIST_RECORDS, 200)
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert 'accept-signature' not in request.headers


def test_list_records_passes_its_arguments(network: FakeSpaceNetwork) -> None:
    for rkey in ('a', 'b', 'c'):
        _put_note(network, BOB_DID, rkey)
    network.put_record(SPACE, BOB_DID, _OTHER, 'd', {'$type': _OTHER})
    reader = make_reader(network)

    first = reader.list_records(BOB_DID, _NOTE, limit=2, exclude_values=True)
    second = reader.list_records(BOB_DID, _NOTE, limit=2, cursor=first.cursor)

    assert [(record.rkey, record.value) for record in first.records] == [('c', None), ('b', None)]
    assert [record.rkey for record in second.records] == ['a']
    assert dict(network.requests_to(_LIST_RECORDS)[0].url.params) == {
        'space': SPACE,
        'repo': BOB_DID,
        'collection': _NOTE,
        'limit': '2',
        'excludeValues': 'true',
    }


def test_list_blobs_asks_the_pds_of_the_repo(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    cids = sorted(network.add_blob(SPACE, ALICE_DID, data) for data in (b'one', b'two', b'three'))
    reader = make_reader(network)

    first = reader.list_blobs(ALICE_DID, limit=2)
    second = reader.list_blobs(ALICE_DID, cursor=first.cursor)

    request = network.requests_to(_LIST_BLOBS)[0]
    assert first.cids == cids[:2]
    assert second.cids == cids[2:]
    assert network.log[-1] == (ALICE_PDS, _LIST_BLOBS, 200)
    assert dict(request.url.params) == {'space': SPACE, 'repo': ALICE_DID, 'limit': '2'}
    assert request.headers['atproto-space-audience'] == ALICE_DID


def test_reads_of_a_repo_require_the_repo(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(ValueError, match='repo to read is required'):
        reader.list_records()
    with pytest.raises(ValueError, match='repo to read is required'):
        reader.list_blobs()
    with pytest.raises(ValueError, match='repo to read is required'):
        next(reader.records())

    assert network.requests == []


def test_writers_follow_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [
        _reply({'repos': [_write(ALICE_DID)], 'cursor': 'page2'}),
        _reply({'repos': [_write(BOB_DID)]}),
    ]
    reader = make_reader(network)

    writers = list(reader.writers())

    assert [writer.repo for writer in writers] == [ALICE_DID, BOB_DID]
    assert _cursors(network, _LIST_WRITERS) == [None, 'page2']


def test_writers_stop_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [
        _reply({'repos': [_write(ALICE_DID)], 'cursor': 'page2'}),
        _reply({'repos': [_write(BOB_DID)], 'cursor': 'page2'}),
    ]
    reader = make_reader(network)

    writers = list(reader.writers())

    assert [writer.repo for writer in writers] == [ALICE_DID, BOB_DID]
    assert network.count(_LIST_WRITERS) == 2


def test_writers_skip_entries_of_an_unknown_kind(network: FakeSpaceNetwork) -> None:
    repos = [
        _write(ALICE_DID),
        {'$type': 'com.example.future#repoFrozen', 'repo': BOB_DID},
        {'$type': _REPO_REMOVED, 'repo': BOB_DID, 'spaceRev': _REV},
    ]
    network.forced_responses[_LIST_WRITERS] = [_reply({'repos': repos}), _reply({'repos': repos})]
    reader = make_reader(network)

    writers = list(reader.writers())

    assert [(type(writer), writer.repo) for writer in writers] == [
        (models.ComAtprotoSpaceDefs.RepoWrite, ALICE_DID),
        (models.ComAtprotoSpaceDefs.RepoRemoved, BOB_DID),
    ]
    assert [type(entry) for entry in reader.list_writers().repos] == [
        models.ComAtprotoSpaceDefs.RepoWrite,
        DotDict,
        models.ComAtprotoSpaceDefs.RepoRemoved,
    ]


def test_writers_start_after_the_cursor(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    writers = list(reader.writers())
    updated = list(reader.writers(writers[0].space_rev))

    assert [writer.repo for writer in writers] == [ALICE_DID, BOB_DID]
    assert [writer.repo for writer in updated] == [BOB_DID]
    assert _cursors(network, _LIST_WRITERS) == [
        None,
        writers[1].space_rev,
        writers[0].space_rev,
        writers[1].space_rev,
    ]


def test_records_follow_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [
        _reply({'records': [_record('a')], 'cursor': 'page2'}),
        _reply({'records': [_record('b')]}),
    ]
    reader = make_reader(network)

    records = list(reader.records(ALICE_DID))

    assert [record.rkey for record in records] == ['a', 'b']
    assert _cursors(network, _LIST_RECORDS) == [None, 'page2']


def test_records_stop_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [
        _reply({'records': [_record('a')], 'cursor': 'page2'}),
        _reply({'records': [_record('b')], 'cursor': 'page2'}),
    ]
    reader = make_reader(network)

    records = list(reader.records(ALICE_DID))

    assert [record.rkey for record in records] == ['a', 'b']
    assert network.count(_LIST_RECORDS) == 2


def test_records_of_a_repo(network: FakeSpaceNetwork) -> None:
    cid = _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    record = next(reader.records(BOB_DID))

    assert (record.repo, record.collection, record.rkey, record.cid) == (BOB_DID, _NOTE, 'b', cid)
    assert record.value == DotDict({'$type': _NOTE, 'text': 'hello'})
    assert record.valid
    assert record.error is None


def test_records_are_validated_against_the_type_of_the_space(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [_reply({'records': _CLASSIFIED})]
    reader = make_reader(network, _GROUP)

    records = {record.rkey: record for record in reader.records(ALICE_DID)}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [
        ('valid', True),
        ('invalid', False),
        ('task', True),
        ('undeclared', False),
        ('mislisted', False),
        ('untyped', False),
        ('excluded', False),
    ]
    assert all(isinstance(record.error, ModelError) for record in records.values() if not record.valid)
    assert isinstance(records['valid'].value, models.AppBskyFeedPost.Record)
    assert isinstance(records['task'].value, models.AppBskyGraphBlock.Record)
    assert records['invalid'].value == {'$type': _POST}
    assert 'text' in str(records['invalid'].error)
    assert str(records['undeclared'].error) == f'{_OTHER} is not a collection of com.example.group spaces'
    assert str(records['mislisted'].error) == f'Record of type {_BLOCK} is stored under collection {_POST}'
    assert str(records['untyped'].error) == 'Record has no type'
    assert records['excluded'].value is None
    assert str(records['excluded'].error) == 'Record has no value'
    assert [request.url.params.get('collection') for request in network.requests_to(_LIST_RECORDS)] == [None]


def test_records_listed_outside_of_the_requested_collection_are_invalid(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [_reply({'records': _CLASSIFIED})]
    reader = make_reader(network, _GROUP)

    records = {record.rkey: record for record in reader.records(ALICE_DID, _POST)}

    assert [(rkey, record.valid) for rkey, record in records.items()] == [
        ('valid', True),
        ('invalid', False),
        ('task', False),
        ('undeclared', False),
        ('mislisted', False),
        ('untyped', False),
        ('excluded', False),
    ]
    assert str(records['task'].error) == f'Record of collection {_BLOCK} is listed under collection {_POST}'
    assert [request.url.params.get('collection') for request in network.requests_to(_LIST_RECORDS)] == [_POST]


def test_records_of_any_collection_are_valid_without_a_type_of_the_space(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [_reply({'records': _CLASSIFIED})]
    reader = make_reader(network)

    records = {record.rkey: record for record in reader.records(ALICE_DID)}

    assert [rkey for rkey, record in records.items() if record.valid] == ['valid', 'task', 'undeclared']
    assert records['undeclared'].value == DotDict({'$type': _OTHER})


def test_credentialed_query_asks_for_a_mac(network: FakeSpaceNetwork) -> None:
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)
    params = models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=BOB_DID)
    kem_key = network.accounts[BOB_DID].did_document.get_kem_key()

    response, encapsulation = run_flow(
        reader._credentialed_query_flow(BOB_DID, _GET_LATEST_COMMIT, params, COMMIT_MAC_PROFILE, kem_key)
    )

    assert encapsulation is not None
    request = network.requests_to(_GET_LATEST_COMMIT)[0]
    commit = get_response_model(response, models.ComAtprotoSpaceGetLatestCommit.Response).commit
    verify_commit_mac(commit, encapsulation, response.headers)
    assert request.headers['accept-signature'] == (
        f'mac=("atproto-space-commit";sf);keyid="{encapsulation.key_share}";tag="atproto-space-commit"'
    )
    assert request.headers['atproto-space-audience'] == BOB_DID


def test_retried_query_asks_for_a_mac_with_another_key_share(network: FakeSpaceNetwork) -> None:
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)
    reader.authorize()
    network.revoke_credentials()
    params = models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=BOB_DID)
    kem_key = network.accounts[BOB_DID].did_document.get_kem_key()

    response, encapsulation = run_flow(
        reader._credentialed_query_flow(BOB_DID, _GET_LATEST_COMMIT, params, COMMIT_MAC_PROFILE, kem_key)
    )

    assert encapsulation is not None
    rejected, retried = network.requests_to(_GET_LATEST_COMMIT)
    commit = get_response_model(response, models.ComAtprotoSpaceGetLatestCommit.Response).commit
    verify_commit_mac(commit, encapsulation, response.headers)
    assert network.statuses(_GET_LATEST_COMMIT) == [401, 200]
    assert encapsulation.key_share in retried.headers['accept-signature']
    assert encapsulation.key_share not in rejected.headers['accept-signature']


def test_concurrent_reads_of_threads_request_one_credential(network: FakeSpaceNetwork) -> None:
    network.delays[_AUTHORIZE] = 0.05
    reader = make_reader(network)

    errors = _run_in_threads(reader.list_writers)

    assert errors == []
    assert network.count(_AUTHORIZE) == 1
    assert network.statuses(_LIST_WRITERS) == [200] * _CONCURRENCY
    assert len(reader._locks) == 0


def test_concurrent_rejections_of_threads_renew_the_credential_once(network: FakeSpaceNetwork) -> None:
    rejected: t.List[str] = []
    barrier = threading.Barrier(_CONCURRENCY, timeout=10)

    def handle(request: httpx.Request) -> httpx.Response:
        # every thread has sent the credential before any of them learns that it is rejected
        if request.headers.get('authorization') in rejected:
            barrier.wait()

        return network.handle(request)

    reader = make_reader(network, request=Request(transport=httpx.MockTransport(handle)))
    rejected.append(_present(reader))
    network.revoke_credentials()
    network.delays[_AUTHORIZE] = 0.05

    errors = _run_in_threads(reader.list_writers)

    assert errors == []
    assert network.count(_AUTHORIZE) == 2
    assert sorted(network.statuses(_LIST_WRITERS)) == [200] * _CONCURRENCY + [401] * _CONCURRENCY
    assert len(reader._locks) == 0
