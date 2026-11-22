import asyncio
import json
import typing as t

import httpx
import pytest
from atproto_client import AsyncClient, models
from atproto_client.exceptions import BadRequestError, NetworkError, UnauthorizedError
from atproto_client.request import AsyncRequest
from atproto_core.uri import SpaceRef
from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
from atproto_identity.exceptions import DidNotFoundError
from atproto_space import AsyncSpaceReader, SpaceType
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
    AsyncFakeIdResolver,
    FakeSpaceNetwork,
    async_fake_id_resolver,
    build_network,
    delegation_token_provider,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_LIST_WRITERS = 'com.atproto.space.listWriters'
_LIST_RECORDS = 'com.atproto.space.listRecords'
_LIST_BLOBS = 'com.atproto.space.listBlobs'

_REPO_WRITE = 'com.atproto.space.defs#repoWrite'
_REPO_REMOVED = 'com.atproto.space.defs#repoRemoved'

_NOTE = 'com.example.note'
_OTHER = 'com.example.other'
_GROUP = SpaceType('com.example.group', 'any', (_NOTE,))

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/src/space-reader.test.ts
_REV = '3jzfcijpj2z2a'
_CID = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'

_CLIENT_ID = 'https://app.test/client-metadata.json'
# the directory of the test suite does not know it
_UNKNOWN_PLC_DID = 'did:plc:kvwvcn5iqfooopmyzvb41234'

_CONCURRENCY = 8


def make_reader(
    network: FakeSpaceNetwork, space_type: t.Optional[SpaceType] = None, **kwargs: t.Any
) -> AsyncSpaceReader:
    kwargs.setdefault('delegation_token_provider', delegation_token_provider(network, ALICE_DID))
    kwargs.setdefault('id_resolver', AsyncFakeIdResolver(network))
    kwargs.setdefault('request', AsyncRequest(transport=network.async_transport))

    return AsyncSpaceReader(SPACE, space_type, **kwargs)


# built when the module is imported, outside of any event loop
_SHARED_NETWORK = build_network()
_SHARED_READER = AsyncSpaceReader(
    SPACE,
    delegation_token_provider=delegation_token_provider(_SHARED_NETWORK, ALICE_DID),
    id_resolver=async_fake_id_resolver(_SHARED_NETWORK),
    request=AsyncRequest(transport=_SHARED_NETWORK.async_transport),
)


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


def _record(rkey: str, collection: str = _NOTE) -> t.Dict[str, t.Any]:
    return {'collection': collection, 'rkey': rkey, 'cid': _CID, 'value': {'$type': collection}}


def _cursors(network: FakeSpaceNetwork, nsid: str) -> t.List[t.Optional[str]]:
    return [request.url.params.get('cursor') for request in network.requests_to(nsid)]


async def _present(reader: AsyncSpaceReader) -> str:
    return f'Atproto-Space-Credential {(await reader.authorize()).token}'


def test_reader_of_a_space_uri() -> None:
    reader = AsyncSpaceReader(SPACE, _GROUP)

    assert reader.ref == SpaceRef(AUTHORITY_DID, 'com.example.group', 'main')
    assert reader.uri == SPACE
    assert reader.space_type is _GROUP
    assert isinstance(reader.request, AsyncRequest)
    assert isinstance(reader._id_resolver.did._cache, AsyncDidInMemoryCache)


@pytest.mark.asyncio
async def test_reader_refuses_a_request_that_carries_a_session() -> None:
    request = AsyncRequest()
    request.add_additional_header('authorization', 'Bearer token')

    with pytest.raises(ValueError, match='must carry no session of an account'):
        AsyncSpaceReader(SPACE, request=request)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        AsyncSpaceReader(SPACE, request=AsyncClient().request)


@pytest.mark.asyncio
async def test_reader_refuses_a_request_that_a_client_was_given_since(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)
    await reader.authorize()
    AsyncClient(request=reader.request)
    network.requests.clear()

    with pytest.raises(ValueError, match='must carry no session of an account'):
        await reader.list_records(BOB_DID)
    with pytest.raises(ValueError, match='must carry no session of an account'):
        await reader.authorize(renew=True)

    assert network.requests == []


@pytest.mark.asyncio
async def test_reads_share_one_credential(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    cid = _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    for _ in range(5):
        await reader.list_writers()
        await reader.list_records(ALICE_DID)
        await reader.list_records(BOB_DID)
        await reader.list_blobs(BOB_DID)

    authorize, *reads = network.requests
    writers = await reader.list_writers()
    records = await reader.list_records(BOB_DID)
    assert network.count(_AUTHORIZE) == 1
    assert len(reads) == 20
    assert 'authorization' not in authorize.headers
    assert {request.headers['authorization'] for request in reads} == {await _present(reader)}
    assert [writer.repo for writer in writers.repos] == [ALICE_DID, BOB_DID]
    assert [(record.rkey, record.cid) for record in records.records] == [('b', cid)]
    assert network.log[:5] == [
        (AUTHORITY_PDS, _AUTHORIZE, 200),
        (AUTHORITY_PDS, _LIST_WRITERS, 200),
        ('https://alice.pds.test', _LIST_RECORDS, 200),
        (BOB_PDS, _LIST_RECORDS, 200),
        (BOB_PDS, _LIST_BLOBS, 200),
    ]


@pytest.mark.asyncio
async def test_authorize_returns_the_credential_until_it_is_renewed(network: FakeSpaceNetwork) -> None:
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    credential = await reader.authorize()
    assert await reader.authorize() is credential

    resolver.did.calls.clear()
    renewed = await reader.authorize(renew=True)
    assert renewed.token != credential.token
    assert await reader.authorize() is renewed
    assert network.count(_AUTHORIZE) == 2
    assert resolver.did.calls == [(AUTHORITY_DID, True)]


@pytest.mark.asyncio
async def test_providers_may_be_coroutine_functions(network: FakeSpaceNetwork) -> None:
    notify = models.ComAtprotoSpaceAuthorizeSpaceSync.Notify(endpoint='https://syncer.example', token='secret')
    private_key = ec.generate_private_key(ec.SECP256R1())

    async def provide_delegation_token(ref: SpaceRef) -> str:
        return network.create_delegation_token(BOB_DID, str(ref))

    async def provide_client_attestation(audience: str) -> str:
        return create_client_attestation(_CLIENT_ID, audience, private_key)

    async def provide_notify_registration(_: SpaceRef) -> 'models.ComAtprotoSpaceAuthorizeSpaceSync.Notify':
        return notify

    reader = make_reader(
        network,
        delegation_token_provider=provide_delegation_token,
        client_attestation_provider=provide_client_attestation,
        notify_registration_provider=provide_notify_registration,
    )

    await reader.authorize()
    await reader.authorize(renew=True)

    requests = network.requests_to(_AUTHORIZE)
    client_attestation = parse_space_token('client_attestation', json.loads(requests[0].content)['clientAttestation'])
    assert network.statuses(_AUTHORIZE) == [200, 200]
    assert [request.content.count(b'"token":"secret"') for request in requests] == [1, 1]
    assert (client_attestation.iss, client_attestation.aud) == (_CLIENT_ID, f'{AUTHORITY_DID}#atproto_pds')


@pytest.mark.asyncio
async def test_rejected_credential_is_renewed_and_the_request_retried(network: FakeSpaceNetwork) -> None:
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)
    await reader.authorize()
    network.revoke_credentials()
    resolver.did.calls.clear()

    assert (await reader.list_records(BOB_DID)).records == []

    rejected, retried = network.requests_to(_LIST_RECORDS)
    assert network.count(_AUTHORIZE) == 2
    assert network.statuses(_LIST_RECORDS) == [401, 200]
    assert retried.headers['authorization'] == await _present(reader)
    assert rejected.headers['authorization'] != retried.headers['authorization']
    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, True), (AUTHORITY_DID, True)]


@pytest.mark.asyncio
async def test_rejected_credential_is_renewed_only_once(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [_reject(), _reject()]
    reader = make_reader(network)

    with pytest.raises(UnauthorizedError, match='401 AuthenticationRequired'):
        await reader.list_writers()

    assert network.count(_AUTHORIZE) == 2
    assert network.count(_LIST_WRITERS) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('body', [{'error': 'SpaceDeleted', 'message': 'Gone'}, {'error': 'SpaceDeleted'}])
async def test_credential_of_a_deleted_space_is_dropped(network: FakeSpaceNetwork, body: t.Dict[str, str]) -> None:
    reader = make_reader(network)
    await reader.authorize()
    network.forced_responses[_AUTHORIZE] = [httpx.Response(400, json=body)]

    with pytest.raises(BadRequestError, match='SpaceDeleted'):
        await reader.authorize(renew=True)

    await reader.authorize()

    assert network.count(_AUTHORIZE) == 3


@pytest.mark.asyncio
async def test_forbidden_request_is_not_retried(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [httpx.Response(403, json={'error': 'Forbidden', 'message': 'Forbidden'})]
    reader = make_reader(network)

    with pytest.raises(UnauthorizedError, match='403 Forbidden'):
        await reader.list_writers()

    assert network.count(_AUTHORIZE) == 1
    assert network.count(_LIST_WRITERS) == 1


@pytest.mark.asyncio
async def test_host_that_redirects_in_a_loop_is_a_network_error(network: FakeSpaceNetwork) -> None:
    async def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(_LIST_RECORDS):
            return httpx.Response(302, headers={'location': str(request.url)})

        return await network.handle_async(request)

    reader = make_reader(network, request=AsyncRequest(transport=httpx.MockTransport(handle)))

    with pytest.raises(NetworkError):
        await reader.list_records(BOB_DID)

    assert network.count(_AUTHORIZE) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('did', [AUTHORITY_DID, BOB_DID], ids=['space authority', 'repo'])
async def test_host_with_a_malformed_pds_endpoint_is_a_network_error(network: FakeSpaceNetwork, did: str) -> None:
    network.accounts[did].pds = 'https://pds.test:8a'
    reader = make_reader(network)

    with pytest.raises(NetworkError):
        await reader.list_records(BOB_DID)

    assert network.count(_LIST_RECORDS) == 0


@pytest.mark.asyncio
async def test_list_writers_passes_the_limit_and_the_cursor(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'b')
    reader = make_reader(network)

    first = await reader.list_writers(limit=1)
    second = await reader.list_writers(limit=1, cursor=first.cursor)

    assert [writer.repo for writer in first.repos] == [ALICE_DID]
    assert [writer.repo for writer in second.repos] == [BOB_DID]


@pytest.mark.asyncio
async def test_list_records_passes_its_arguments(network: FakeSpaceNetwork) -> None:
    for rkey in ('a', 'b', 'c'):
        _put_note(network, BOB_DID, rkey)
    network.put_record(SPACE, BOB_DID, _OTHER, 'd', {'$type': _OTHER})
    reader = make_reader(network)

    first = await reader.list_records(BOB_DID, _NOTE, limit=2, exclude_values=True)
    second = await reader.list_records(BOB_DID, _NOTE, limit=2, cursor=first.cursor)

    assert [(record.rkey, record.value) for record in first.records] == [('c', None), ('b', None)]
    assert [record.rkey for record in second.records] == ['a']
    assert dict(network.requests_to(_LIST_RECORDS)[0].url.params) == {
        'space': SPACE,
        'repo': BOB_DID,
        'collection': _NOTE,
        'limit': '2',
        'excludeValues': 'true',
    }


@pytest.mark.asyncio
async def test_list_blobs_asks_the_pds_of_the_repo(network: FakeSpaceNetwork) -> None:
    _put_note(network, ALICE_DID, 'a')
    cids = sorted(network.add_blob(SPACE, ALICE_DID, data) for data in (b'one', b'two', b'three'))
    reader = make_reader(network)

    first = await reader.list_blobs(ALICE_DID, limit=2)
    second = await reader.list_blobs(ALICE_DID, cursor=first.cursor)

    request = network.requests_to(_LIST_BLOBS)[0]
    assert first.cids == cids[:2]
    assert second.cids == cids[2:]
    assert network.log[-1] == (ALICE_PDS, _LIST_BLOBS, 200)
    assert dict(request.url.params) == {'space': SPACE, 'repo': ALICE_DID, 'limit': '2'}
    assert request.headers['atproto-space-audience'] == ALICE_DID


@pytest.mark.asyncio
async def test_writers_follow_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [
        _reply({'repos': [_write(ALICE_DID)], 'cursor': 'page2'}),
        _reply({'repos': [_write(BOB_DID)]}),
    ]
    reader = make_reader(network)

    writers = [writer async for writer in reader.writers()]

    assert [writer.repo for writer in writers] == [ALICE_DID, BOB_DID]
    assert _cursors(network, _LIST_WRITERS) == [None, 'page2']


@pytest.mark.asyncio
async def test_writers_stop_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_WRITERS] = [
        _reply({'repos': [_write(ALICE_DID)], 'cursor': 'page2'}),
        _reply({'repos': [_write(BOB_DID)], 'cursor': 'page2'}),
    ]
    reader = make_reader(network)

    writers = [writer async for writer in reader.writers('page1')]

    assert [writer.repo for writer in writers] == [ALICE_DID, BOB_DID]
    assert _cursors(network, _LIST_WRITERS) == ['page1', 'page2']


@pytest.mark.asyncio
async def test_writers_skip_entries_of_an_unknown_kind(network: FakeSpaceNetwork) -> None:
    repos = [
        _write(ALICE_DID),
        {'$type': 'com.example.future#repoFrozen', 'repo': BOB_DID},
        {'$type': _REPO_REMOVED, 'repo': BOB_DID, 'spaceRev': _REV},
    ]
    network.forced_responses[_LIST_WRITERS] = [_reply({'repos': repos})]
    reader = make_reader(network)

    writers = [writer async for writer in reader.writers()]

    assert [(type(writer), writer.repo) for writer in writers] == [
        (models.ComAtprotoSpaceDefs.RepoWrite, ALICE_DID),
        (models.ComAtprotoSpaceDefs.RepoRemoved, BOB_DID),
    ]


@pytest.mark.asyncio
async def test_records_follow_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [
        _reply({'records': [_record('a')], 'cursor': 'page2'}),
        _reply({'records': [_record('b', _OTHER)]}),
    ]
    reader = make_reader(network, _GROUP)

    records = [record async for record in reader.records(ALICE_DID)]

    assert [(record.repo, record.rkey, record.valid) for record in records] == [
        (ALICE_DID, 'a', True),
        (ALICE_DID, 'b', False),
    ]
    assert str(records[1].error) == f'{_OTHER} is not a collection of com.example.group spaces'
    assert _cursors(network, _LIST_RECORDS) == [None, 'page2']


@pytest.mark.asyncio
async def test_records_stop_when_the_host_repeats_the_cursor(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [
        _reply({'records': [_record('a')], 'cursor': 'page2'}),
        _reply({'records': [_record('b')], 'cursor': 'page2'}),
    ]
    reader = make_reader(network)

    records = [record async for record in reader.records(ALICE_DID, _NOTE)]

    assert [record.rkey for record in records] == ['a', 'b']
    assert network.count(_LIST_RECORDS) == 2


@pytest.mark.asyncio
async def test_records_listed_outside_of_the_requested_collection_are_invalid(network: FakeSpaceNetwork) -> None:
    network.forced_responses[_LIST_RECORDS] = [_reply({'records': [_record('a'), _record('b', _OTHER)]})]
    reader = make_reader(network)

    records = [record async for record in reader.records(ALICE_DID, _NOTE)]

    assert [(record.rkey, record.valid) for record in records] == [('a', True), ('b', False)]
    assert str(records[1].error) == f'Record of collection {_OTHER} is listed under collection {_NOTE}'
    assert [request.url.params.get('collection') for request in network.requests_to(_LIST_RECORDS)] == [_NOTE]


@pytest.mark.asyncio
async def test_reads_of_a_repo_require_the_repo(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.list_records()
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.list_blobs()
    with pytest.raises(ValueError, match='repo to read is required'):
        _ = [record async for record in reader.records()]

    assert network.requests == []


@pytest.mark.asyncio
async def test_unknown_audience_is_not_found_by_the_default_resolver(network: FakeSpaceNetwork) -> None:
    reader = AsyncSpaceReader(SPACE, request=AsyncRequest(transport=network.async_transport))

    with pytest.raises(DidNotFoundError):
        await reader.list_records(_UNKNOWN_PLC_DID)

    assert network.requests == []


@pytest.mark.asyncio
async def test_reader_built_outside_of_an_event_loop_requests_one_credential_for_concurrent_tasks() -> None:
    _SHARED_NETWORK.delays[_AUTHORIZE] = 0.05

    responses = await asyncio.gather(*[_SHARED_READER.list_writers() for _ in range(_CONCURRENCY)])

    assert len(responses) == _CONCURRENCY
    assert _SHARED_NETWORK.count(_AUTHORIZE) == 1
    assert _SHARED_NETWORK.statuses(_LIST_WRITERS) == [200] * _CONCURRENCY
    assert len(_SHARED_READER._locks) == 0


@pytest.mark.asyncio
async def test_concurrent_rejections_of_tasks_renew_the_credential_once(network: FakeSpaceNetwork) -> None:
    rejected: t.List[str] = []
    waiting: t.List[httpx.Request] = []
    sent = asyncio.Event()

    async def handle(request: httpx.Request) -> httpx.Response:
        # every task has sent the credential before any of them learns that it is rejected
        if request.headers.get('authorization') in rejected:
            waiting.append(request)
            if len(waiting) == _CONCURRENCY:
                sent.set()

            await asyncio.wait_for(sent.wait(), 10)

        return await network.handle_async(request)

    reader = make_reader(network, request=AsyncRequest(transport=httpx.MockTransport(handle)))
    rejected.append(await _present(reader))
    network.revoke_credentials()
    network.delays[_AUTHORIZE] = 0.05

    await asyncio.gather(*[reader.list_writers() for _ in range(_CONCURRENCY)])

    assert network.count(_AUTHORIZE) == 2
    assert sorted(network.statuses(_LIST_WRITERS)) == [200] * _CONCURRENCY + [401] * _CONCURRENCY
    assert len(reader._locks) == 0


def test_reader_is_used_in_one_event_loop_after_another(network: FakeSpaceNetwork) -> None:
    network.delays[_AUTHORIZE] = 0.01
    reader = make_reader(network)

    async def renew() -> None:
        await asyncio.gather(reader.authorize(renew=True), reader.authorize(renew=True))

    asyncio.run(renew())
    asyncio.run(renew())

    assert network.count(_AUTHORIZE) == 4
    assert len(reader._locks) == 0
