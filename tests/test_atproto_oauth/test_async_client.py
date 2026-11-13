import asyncio
import contextlib
import typing as t

import httpx
import pytest
from atproto_crypto.jwk import generate_p256_jwk
from atproto_oauth import AsyncOAuthClient, MemoryStore, OAuthCallbackResult, OAuthSessionData
from atproto_oauth.exceptions import (
    AuthMethodUnsatisfiableError,
    OAuthCallbackError,
    OAuthResponseError,
    TokenRefreshError,
    TokenRevokedError,
    UnsupportedAuthServerError,
)

from tests.test_atproto_oauth.fake_server import (
    BOB_DID,
    DID,
    HANDLE,
    ISSUER,
    PDS,
    VICTIM_DID,
    Account,
    AsyncFakeIdResolver,
    FakeServer,
    async_fake_id_resolver,
    get_stored_session,
    make_stale,
    record_causes,
)

REDIRECT_URI = 'http://127.0.0.1:8765/callback'
SCOPE = 'atproto transition:generic'


def make_client(server: FakeServer, **kwargs: t.Any) -> AsyncOAuthClient:
    kwargs.setdefault('id_resolver', AsyncFakeIdResolver(server))
    return AsyncOAuthClient.loopback(REDIRECT_URI, SCOPE, transport=server.transport, **kwargs)


async def login(
    client: AsyncOAuthClient, server: FakeServer, identifier: str = HANDLE, **kwargs: t.Any
) -> OAuthCallbackResult[t.Any]:
    return await client.callback(server.approve(await client.authorize(identifier, **kwargs)))


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


@pytest.fixture(autouse=True)
def _no_refresh_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('atproto_oauth._base.CONCURRENT_REFRESH_DELAY', 0)


@pytest.mark.asyncio
async def test_loopback_login(server: FakeServer) -> None:
    client = make_client(server)

    result = await login(client, server, state='app-state')

    assert result.state == 'app-state'
    assert result.session.did == DID
    assert result.session.pds_endpoint == PDS
    info = await result.session.get_token_info()
    assert (info.sub, info.iss, info.aud, info.scope) == (DID, ISSUER, PDS, SCOPE)
    assert server.statuses('/oauth/par') == [400, 201]

    await client.close()


@pytest.mark.asyncio
async def test_confidential_client_and_key_removal(server: FakeServer) -> None:
    store: MemoryStore[OAuthSessionData] = MemoryStore()
    key = generate_p256_jwk(kid='key-1')

    def make(keys: t.List[t.Dict[str, t.Any]]) -> AsyncOAuthClient:
        client = AsyncOAuthClient.confidential(
            'https://app.test/client-metadata.json',
            'https://app.test/callback',
            SCOPE,
            keys,
            session_store=store,
            transport=server.transport,
            id_resolver=async_fake_id_resolver(server),
        )
        server.client_jwks = client.jwks
        return client

    client = make([key])
    await login(client, server)
    await client.restore(DID, refresh=True)
    assert server.statuses('/oauth/token') == [200, 200]

    with pytest.raises(AuthMethodUnsatisfiableError):
        await make([generate_p256_jwk(kid='key-2')]).restore(DID, refresh=True)

    assert store.get(DID) is None


@pytest.mark.asyncio
async def test_asynchronous_stores_and_callbacks(server: FakeServer) -> None:
    class AsyncDictStore:
        def __init__(self) -> None:
            self.data: t.Dict[str, t.Any] = {}

        async def get(self, key: str) -> t.Any:
            await asyncio.sleep(0)
            return self.data.get(key)

        async def set(self, key: str, value: t.Any) -> None:
            await asyncio.sleep(0)
            self.data[key] = value.to_dict()

        async def delete(self, key: str) -> None:
            await asyncio.sleep(0)
            self.data.pop(key, None)

    states, sessions = AsyncDictStore(), AsyncDictStore()
    events: t.List[str] = []

    async def on_updated(did: str, data: OAuthSessionData) -> None:
        events.append(f'updated:{did}')

    def on_deleted(did: str, cause: BaseException) -> None:
        events.append(f'deleted:{type(cause).__name__}')

    client = make_client(
        server,
        state_store=states,
        session_store=sessions,
        on_session_updated=on_updated,
        on_session_deleted=on_deleted,
    )

    await login(client, server)
    assert states.data == {}
    assert sessions.data[DID]['token_set']['sub'] == DID

    await client.restore(DID, refresh=True)
    await client.revoke(DID)

    assert sessions.data == {}
    assert events == [f'updated:{DID}', f'updated:{DID}', 'deleted:TokenRevokedError']


@pytest.mark.asyncio
async def test_callback_errors(server: FakeServer) -> None:
    client = make_client(server)

    with pytest.raises(OAuthCallbackError) as e:
        await client.callback(server.deny(await client.authorize(HANDLE, state='app-state')))

    assert e.value.state == 'app-state'
    assert e.value.error == 'access_denied'

    params = server.approve(await client.authorize(HANDLE))
    await client.callback(params)
    with pytest.raises(OAuthCallbackError, match='Unknown authorization request'):
        await client.callback(params)

    params = server.approve(await client.authorize(HANDLE))
    with pytest.raises(OAuthCallbackError, match='another issuer'):
        await client.callback({**params, 'iss': 'https://evil.test'})


@pytest.mark.asyncio
async def test_token_response_is_validated_and_tokens_revoked(server: FakeServer) -> None:
    client = make_client(server)
    server.token_response_overrides = {'token_type': 'Bearer'}

    with pytest.raises(OAuthCallbackError, match='token type'):
        await login(client, server)

    assert len(server.revoked_tokens) == 1


@pytest.mark.asyncio
async def test_unexpected_or_foreign_account_is_rejected(server: FakeServer) -> None:
    server.accounts[BOB_DID] = Account(BOB_DID, 'bob.test', PDS)
    server.accounts[VICTIM_DID] = Account(VICTIM_DID, 'victim.test', 'https://other-pds.test')
    client = make_client(server)

    with pytest.raises(OAuthCallbackError, match='not the expected'):
        await client.callback(server.approve(await client.authorize(HANDLE), sub=BOB_DID))

    with pytest.raises(OAuthCallbackError):
        await client.callback(server.approve(await client.authorize(PDS), sub=VICTIM_DID))

    assert len(server.revoked_tokens) == 2
    assert client._session_store.get(BOB_DID) is None
    assert client._session_store.get(VICTIM_DID) is None


@pytest.mark.asyncio
async def test_new_login_replaces_and_revokes_the_previous_session(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client = make_client(server, on_session_deleted=record_causes(deleted))

    await login(client, server)
    first_token = get_stored_session(client._session_store).token_set.access_token
    await login(client, server)

    assert server.revoked_tokens == [first_token]
    assert [type(cause) for cause in deleted] == [TokenRevokedError]


@pytest.mark.asyncio
async def test_refresh_behaviour(server: FakeServer) -> None:
    client = make_client(server)
    session = (await login(client, server)).session

    await client.restore(DID)
    assert server.count('/oauth/token') == 1

    server.expires_in = 5
    await client.restore(DID, refresh=True)
    server.expires_in = 3600
    await client.restore(DID)
    assert server.count('/oauth/token') == 3

    server.forced_responses['/oauth/token'] = httpx.Response(503, text='down')
    with pytest.raises(OAuthResponseError):
        await session.get_token_info(True)

    assert client._session_store.get(DID) is not None
    del server.forced_responses['/oauth/token']

    server.grants[-1].revoked = True
    with pytest.raises(TokenRefreshError, match='Invalid refresh token'):
        await session.get_token_info(True)

    assert client._session_store.get(DID) is None

    with pytest.raises(TokenRefreshError, match='No session is stored'):
        await client.restore(DID)


@pytest.mark.asyncio
async def test_refresh_adopts_tokens_refreshed_by_another_process(
    server: FakeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    store: MemoryStore[OAuthSessionData] = MemoryStore()
    first = make_client(server, session_store=store)
    second = make_client(server, session_store=store)

    session = (await login(first, server)).session
    stale = get_stored_session(store)
    await second.restore(DID, refresh=True)
    fresh = get_stored_session(store)
    store.set(DID, stale)

    # this process reads the stale session, fails to refresh, then finds what the other one stored
    reads = iter([stale, fresh])

    def read(key: str) -> OAuthSessionData:
        return next(reads)

    monkeypatch.setattr(store, 'get', read)

    assert (await session.get_token_info(True)).sub == DID
    assert session._data == fresh


@pytest.mark.asyncio
async def test_concurrent_restores_refresh_once_under_an_external_lock(server: FakeServer) -> None:
    held: t.List[str] = []

    @contextlib.asynccontextmanager
    async def lock(did: str) -> t.AsyncGenerator[None, None]:
        held.append('enter')
        yield
        held.append('exit')

    client = make_client(server, lock=lock)
    await login(client, server)

    client._session_store.set(DID, make_stale(get_stored_session(client._session_store)))
    held.clear()

    sessions = await asyncio.gather(*[client.restore(DID) for _ in range(16)])

    assert {session.did for session in sessions} == {DID}
    assert server.count('/oauth/token') == 2
    assert held == ['enter', 'exit'] * 16
    assert len(client._locks) == 0


@pytest.mark.asyncio
async def test_invalid_server_metadata(server: FakeServer) -> None:
    server.server_metadata_overrides = {'issuer': 'https://evil.test'}

    with pytest.raises(UnsupportedAuthServerError):
        await make_client(server).authorize(HANDLE)


@pytest.mark.asyncio
async def test_restore_by_handle(server: FakeServer) -> None:
    client = make_client(server)
    await login(client, server)

    assert (await client.restore(HANDLE)).did == DID


@pytest.mark.asyncio
async def test_abandoned_authorizations_are_bounded(server: FakeServer, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('atproto_oauth.async_client.DEFAULT_MAX_PENDING_AUTHORIZATIONS', 3)
    client = make_client(server)

    urls = [await client.authorize(HANDLE) for _ in range(5)]

    assert len(client._state_store._values) == 3
    with pytest.raises(OAuthCallbackError, match='Unknown authorization request'):
        await client.callback(server.approve(urls[0]))


@pytest.mark.asyncio
async def test_every_session_operation_takes_the_external_lock(server: FakeServer) -> None:
    held: t.List[str] = []

    @contextlib.asynccontextmanager
    async def lock(did: str) -> t.AsyncGenerator[None, None]:
        held.append(did)
        yield

    client = make_client(server, lock=lock)

    await login(client, server)
    assert held == [DID]

    await client._drop_rejected_session(DID, get_stored_session(client._session_store).token_set)
    await client.revoke(DID)
    assert held == [DID, DID, DID]
