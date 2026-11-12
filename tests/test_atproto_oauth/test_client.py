import contextlib
import json
import threading
import time
import typing as t
from urllib.parse import parse_qs

import httpx
import pytest
import typing_extensions as te
from atproto_crypto.jwk import generate_p256_jwk
from atproto_oauth import MemoryStore, OAuthCallbackResult, OAuthClient, OAuthSessionData, OAuthStateData
from atproto_oauth import _base as oauth_base
from atproto_oauth.exceptions import (
    AuthMethodUnsatisfiableError,
    OAuthCallbackError,
    OAuthRequestError,
    OAuthResolverError,
    OAuthResponseError,
    TokenRefreshError,
    TokenRevokedError,
    UnsafeUrlError,
    UnsupportedAuthServerError,
)

from tests.test_atproto_oauth.fake_server import (
    BOB_DID,
    DID,
    HANDLE,
    ISSUER,
    PDS,
    UNKNOWN_DID,
    VICTIM_DID,
    Account,
    FakeIdResolver,
    FakeServer,
    decode_jwt,
    get_stored_session,
    make_stale,
    record_access_tokens,
    record_causes,
    record_deletions,
)

REDIRECT_URI = 'http://127.0.0.1:8765/callback'
SCOPE = 'atproto transition:generic'
CLIENT_ID = 'https://app.test/client-metadata.json'


def make_client(server: FakeServer, **kwargs: t.Any) -> OAuthClient:
    kwargs.setdefault('id_resolver', FakeIdResolver(server))
    return OAuthClient.loopback(REDIRECT_URI, SCOPE, transport=server.transport, **kwargs)


def login(
    client: OAuthClient, server: FakeServer, identifier: str = HANDLE, **kwargs: t.Any
) -> OAuthCallbackResult[t.Any]:
    return client.callback(server.approve(client.authorize(identifier, **kwargs)))


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


@pytest.fixture(autouse=True)
def _no_refresh_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(oauth_base, 'CONCURRENT_REFRESH_DELAY', 0)


def test_loopback_login(server: FakeServer) -> None:
    client = make_client(server)

    url = client.authorize(HANDLE, state='app-state')
    assert url.startswith(f'{ISSUER}/oauth/authorize?client_id=http%3A%2F%2Flocalhost%3F')

    result = client.callback(server.approve(url))

    assert result.state == 'app-state'
    assert result.session.did == DID
    assert result.session.pds_endpoint == PDS
    assert result.session.permissions.allows_repo('app.bsky.feed.post', 'create')

    info = result.session.get_token_info()
    assert (info.sub, info.iss, info.aud, info.scope) == (DID, ISSUER, PDS, SCOPE)
    assert info.expired is False
    assert info.expires_at is not None
    assert 3500 < info.expires_at.timestamp() - time.time() <= 3600


def test_par_request_content(server: FakeServer) -> None:
    client = make_client(server)
    client.authorize(HANDLE, prompt='login')

    (request,) = server.par_requests.values()
    assert request['client_id'] == client.client_id
    assert request['redirect_uri'] == REDIRECT_URI
    assert request['scope'] == SCOPE
    assert request['login_hint'] == HANDLE
    assert request['prompt'] == 'login'
    assert request['code_challenge_method'] == 'S256'
    assert len(request['state']) >= 22
    assert 'client_assertion' not in request

    # the first PAR request has no nonce yet and is repeated with the one the server sent
    assert server.statuses('/oauth/par') == [400, 201]


def test_nonce_is_reused_across_requests(server: FakeServer) -> None:
    client = make_client(server)
    login(client, server)

    assert server.statuses('/oauth/token') == [200]

    server.as_nonce = 'as-nonce-2'
    client.restore(DID, refresh=True)
    assert server.statuses('/oauth/token') == [200, 400, 200]


def test_login_with_did_and_with_service_url(server: FakeServer) -> None:
    client = make_client(server)

    assert login(client, server, DID).session.did == DID
    assert next(iter(server.codes.values()), None) is None

    client.authorize(PDS)
    (request,) = server.par_requests.values()
    assert 'login_hint' not in request

    assert login(client, server, PDS).session.did == DID
    assert login(client, server, ISSUER).session.did == DID


def test_identity_is_verified_without_cache_after_token_response(server: FakeServer) -> None:
    id_resolver = FakeIdResolver(server)
    client = make_client(server, id_resolver=id_resolver)
    login(client, server)

    assert id_resolver.did.calls == [(DID, False), (DID, True)]


def test_confidential_client(server: FakeServer) -> None:
    keys = [generate_p256_jwk(kid='key-1')]
    client = OAuthClient.confidential(
        CLIENT_ID,
        'https://app.test/callback',
        SCOPE,
        keys,
        transport=server.transport,
        id_resolver=FakeIdResolver(server),
    )
    server.client_jwks = client.jwks

    assert client.client_metadata['token_endpoint_auth_method'] == 'private_key_jwt'
    assert client.client_metadata['jwks'] == client.jwks
    assert all('d' not in key for key in client.jwks['keys'])

    result = login(client, server)
    assert result.session.did == DID

    stored = get_stored_session(client._session_store)
    assert stored.auth_method.to_dict() == {'method': 'private_key_jwt', 'kid': 'key-1'}

    client.restore(DID, refresh=True)
    assert server.statuses('/oauth/token') == [200, 200]


def test_confidential_client_keeps_the_key_of_the_session_after_rotation(server: FakeServer) -> None:
    store: MemoryStore[OAuthSessionData] = MemoryStore()
    old_key, new_key = generate_p256_jwk(kid='old'), generate_p256_jwk(kid='new')

    def make(keys: t.List[t.Dict[str, t.Any]]) -> OAuthClient:
        client = OAuthClient.confidential(
            CLIENT_ID,
            'https://app.test/callback',
            SCOPE,
            keys,
            session_store=store,
            transport=server.transport,
            id_resolver=FakeIdResolver(server),
        )
        server.client_jwks = client.jwks
        return client

    login(make([old_key]), server)

    rotated = make([new_key, old_key])
    rotated.restore(DID, refresh=True)
    header, _ = decode_jwt(_last_form(server)['client_assertion'])
    assert header['kid'] == 'old'

    without_old_key = make([new_key])
    deleted: t.List[t.Tuple[str, BaseException]] = []
    without_old_key._on_session_deleted = record_deletions(deleted)
    with pytest.raises(AuthMethodUnsatisfiableError):
        without_old_key.restore(DID, refresh=True)

    assert store.get(DID) is None
    assert isinstance(deleted[0][1], AuthMethodUnsatisfiableError)


def _last_form(server: FakeServer) -> t.Dict[str, str]:
    request = next(r for r in reversed(server.requests) if r.url.path.startswith('/oauth/'))
    return {name: values[0] for name, values in parse_qs(request.content.decode()).items()}


def test_authorize_overrides(server: FakeServer) -> None:
    other = 'http://127.0.0.1/other'
    client = OAuthClient.loopback(
        [REDIRECT_URI, other], SCOPE, transport=server.transport, id_resolver=FakeIdResolver(server)
    )

    result = client.callback(server.approve(client.authorize(HANDLE, redirect_uri=other, scope='atproto')))
    assert result.session.get_token_info().scope == 'atproto'

    with pytest.raises(ValueError, match='not registered'):
        client.authorize(HANDLE, redirect_uri='http://127.0.0.1/unknown')

    with pytest.raises(ValueError, match='not registered'):
        client.authorize(HANDLE, scope='atproto transition:chat.bsky')

    with pytest.raises(ValueError, match='must include'):
        client.authorize(HANDLE, scope='transition:generic')

    with pytest.raises(ValueError, match='can not be overridden'):
        client.authorize(HANDLE, client_id='https://evil.test')


def test_callback_is_single_use_and_rejects_unknown_state(server: FakeServer) -> None:
    client = make_client(server)
    params = server.approve(client.authorize(HANDLE))
    client.callback(params)

    with pytest.raises(OAuthCallbackError, match='Unknown authorization request'):
        client.callback(params)

    with pytest.raises(OAuthCallbackError, match='no "state"'):
        client.callback({'code': 'abc', 'iss': ISSUER})

    with pytest.raises(OAuthCallbackError, match='JARM'):
        client.callback({'response': 'jwt'})


def test_callback_reports_denial_with_app_state(server: FakeServer) -> None:
    client = make_client(server)

    with pytest.raises(OAuthCallbackError) as e:
        client.callback(server.deny(client.authorize(HANDLE, state='app-state')))

    assert e.value.state == 'app-state'
    assert e.value.error == 'access_denied'
    assert e.value.error_description == 'The user denied the request'
    assert server.count('/oauth/token') == 0


@pytest.mark.parametrize(
    ('change', 'message'),
    [
        ({'iss': None}, 'no "iss"'),
        ({'iss': 'https://evil.test'}, 'another issuer'),
        ({'code': None}, 'no "code"'),
    ],
)
def test_callback_rejects_bad_parameters(server: FakeServer, change: t.Dict[str, t.Any], message: str) -> None:
    client = make_client(server)
    params = {**server.approve(client.authorize(HANDLE, state='app-state')), **change}
    params = {name: value for name, value in params.items() if value is not None}

    with pytest.raises(OAuthCallbackError, match=message) as e:
        client.callback(params)

    assert e.value.state == 'app-state'
    assert server.count('/oauth/token') == 0


def test_callback_rejects_expired_state_whatever_the_store(server: FakeServer) -> None:
    states: t.Dict[str, OAuthStateData] = {}

    class DictStore:
        def get(self, key: str) -> t.Optional[OAuthStateData]:
            return states.get(key)

        def set(self, key: str, value: OAuthStateData) -> None:
            states[key] = value

        def delete(self, key: str) -> None:
            states.pop(key, None)

    client = make_client(server, state_store=DictStore(), state_ttl=0.05)
    params = server.approve(client.authorize(HANDLE))
    time.sleep(0.1)

    with pytest.raises(OAuthCallbackError, match='expired'):
        client.callback(params)

    assert states == {}


def test_stores_may_hold_plain_dicts(server: FakeServer) -> None:
    states: t.Dict[str, t.Dict[str, t.Any]] = {}
    sessions: t.Dict[str, t.Dict[str, t.Any]] = {}

    class JsonStore:
        def __init__(self, data: t.Dict[str, t.Dict[str, t.Any]]) -> None:
            self.data = data

        def get(self, key: str) -> t.Optional[t.Dict[str, t.Any]]:
            return self.data.get(key)

        def set(self, key: str, value: t.Any) -> None:
            self.data[key] = json.loads(json.dumps(value.to_dict()))

        def delete(self, key: str) -> None:
            self.data.pop(key, None)

    client = make_client(server, state_store=JsonStore(states), session_store=JsonStore(sessions))
    login(client, server)

    assert sessions[DID]['token_set']['sub'] == DID
    assert sessions[DID]['dpop_jwk']['kty'] == 'EC'
    assert client.restore(DID, refresh=True).did == DID


@pytest.mark.parametrize(
    ('overrides', 'message'),
    [
        ({'token_type': 'Bearer'}, 'token type'),
        ({'sub': 'alice.test'}, 'DID'),
        ({'scope': 'transition:generic'}, 'atproto'),
        ({'scope': None}, 'atproto'),
        ({'id_token': 'jwt'}, 'id_token'),
        ({'access_token': None}, 'access_token'),
    ],
)
def test_token_response_is_validated_and_tokens_revoked(
    server: FakeServer, overrides: t.Dict[str, t.Any], message: str
) -> None:
    client = make_client(server)
    server.token_response_overrides = overrides

    with pytest.raises(OAuthCallbackError, match=message):
        login(client, server)

    assert client._session_store.get(DID) is None
    if overrides.get('access_token', '') is not None:
        assert len(server.revoked_tokens) == 1


def test_account_other_than_the_expected_one_is_rejected(server: FakeServer) -> None:
    server.accounts[BOB_DID] = Account(BOB_DID, 'bob.test', PDS)
    client = make_client(server)

    with pytest.raises(OAuthCallbackError, match='not the expected'):
        client.callback(server.approve(client.authorize(HANDLE), sub=BOB_DID))

    assert len(server.revoked_tokens) == 1
    assert client._session_store.get(BOB_DID) is None

    # nothing is expected when the flow started from a server
    result = client.callback(server.approve(client.authorize(PDS), sub=BOB_DID))
    assert result.session.did == BOB_DID


def test_account_served_by_another_authorization_server_is_rejected(server: FakeServer) -> None:
    # the authorization server claims an account whose DID document points elsewhere
    server.accounts[VICTIM_DID] = Account(VICTIM_DID, 'victim.test', 'https://other-pds.test')
    client = make_client(server)

    with pytest.raises(OAuthCallbackError):
        client.callback(server.approve(client.authorize(PDS), sub=VICTIM_DID))

    assert len(server.revoked_tokens) == 1
    assert client._session_store.get(VICTIM_DID) is None


def test_new_login_replaces_and_revokes_the_previous_session(server: FakeServer) -> None:
    updated: t.List[str] = []
    deleted: t.List[t.Tuple[str, BaseException]] = []
    client = make_client(
        server,
        on_session_updated=record_access_tokens(updated),
        on_session_deleted=record_deletions(deleted),
    )

    first = login(client, server).session.get_token_info(False)
    assert first.sub == DID
    first_token = updated[0]

    login(client, server)

    assert server.revoked_tokens == [first_token]
    assert len(updated) == 2
    assert [type(cause) for _, cause in deleted] == [TokenRevokedError]
    assert get_stored_session(client._session_store).token_set.access_token == updated[1]


def test_restore_refreshes_only_stale_tokens(server: FakeServer) -> None:
    client = make_client(server)
    login(client, server)

    client.restore(DID)
    assert server.count('/oauth/token') == 1

    server.expires_in = 5
    client.restore(DID, refresh=True)
    assert server.count('/oauth/token') == 2

    # expires within the leeway, so it is refreshed on the next use
    server.expires_in = 3600
    assert client.restore(DID).get_token_info().expired is False
    assert server.count('/oauth/token') == 3

    # never refreshed on request
    server.expires_in = 5
    client.restore(DID, refresh=True)
    assert client.restore(DID, refresh=False).did == DID
    assert server.count('/oauth/token') == 4


def test_restore_without_session(server: FakeServer) -> None:
    client = make_client(server)

    with pytest.raises(TokenRefreshError, match='No session is stored') as e:
        client.restore(DID)

    assert e.value.did == DID


def test_refresh_follows_pds_migration_and_verifies_issuer_first(server: FakeServer) -> None:
    id_resolver = FakeIdResolver(server)
    client = make_client(server, id_resolver=id_resolver)
    session = login(client, server).session

    id_resolver.did.calls.clear()
    session.get_token_info(True)
    assert id_resolver.did.calls == [(DID, True)]

    # the PDS the account moved to can not be reached: nothing is concluded and the session is kept
    server.accounts[DID].pds = 'https://other-pds.test'
    deleted: t.List[BaseException] = []
    client._on_session_deleted = record_causes(deleted)
    tokens_before = server.count('/oauth/token')

    with pytest.raises(OAuthResolverError):
        session.get_token_info(True)

    assert server.count('/oauth/token') == tokens_before
    assert deleted == []
    assert client._session_store.get(DID) is not None


def test_session_of_an_account_that_left_the_authorization_server_is_deleted(
    server: FakeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    deleted: t.List[BaseException] = []
    client = make_client(server, on_session_deleted=record_causes(deleted))
    session = login(client, server).session
    tokens_before = server.count('/oauth/token')

    def no_longer_served(resolved: t.Any, issuer: str) -> None:
        return None

    monkeypatch.setattr('atproto_oauth._flow.get_verified_pds', no_longer_served)

    with pytest.raises(TokenRefreshError, match='no longer served'):
        session.get_token_info(True)

    # the refresh token is not spent on a server that no longer speaks for the account
    assert server.count('/oauth/token') == tokens_before
    assert len(deleted) == 1
    assert client._session_store.get(DID) is None


def test_refresh_failure_deletes_the_session(server: FakeServer) -> None:
    deleted: t.List[t.Tuple[str, BaseException]] = []
    client = make_client(server, on_session_deleted=record_deletions(deleted))
    session = login(client, server).session

    server.grants[-1].revoked = True
    with pytest.raises(TokenRefreshError, match='Invalid refresh token'):
        session.get_token_info(True)

    assert client._session_store.get(DID) is None
    assert [did for did, _ in deleted] == [DID]
    assert isinstance(deleted[0][1], TokenRefreshError)
    assert isinstance(deleted[0][1].__cause__, OAuthResponseError)


def test_refresh_adopts_tokens_refreshed_by_another_process(
    server: FakeServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    store: MemoryStore[OAuthSessionData] = MemoryStore()
    first = make_client(server, session_store=store)
    second = make_client(server, session_store=store)

    session = login(first, server).session
    stale = get_stored_session(store)

    # the other process refreshes, then this one tries with the spent refresh token
    second.restore(DID, refresh=True)
    fresh = get_stored_session(store)
    store.set(DID, stale)

    # this process reads the stale session, fails to refresh, then finds what the other one stored
    reads = iter([stale, fresh])

    def read(key: str) -> OAuthSessionData:
        return next(reads)

    monkeypatch.setattr(store, 'get', read)

    info = session.get_token_info(True)
    assert info.sub == DID
    assert session._data == fresh


def test_refresh_without_refresh_token(server: FakeServer) -> None:
    server.issue_refresh_tokens = False
    client = make_client(server)
    session = login(client, server).session

    with pytest.raises(TokenRefreshError, match='No refresh token'):
        session.get_token_info(True)

    assert client._session_store.get(DID) is None


def test_network_failure_during_refresh_keeps_the_session(server: FakeServer) -> None:
    client = make_client(server)
    session = login(client, server).session

    server.forced_responses['/oauth/token'] = httpx.Response(503, text='down')
    with pytest.raises(OAuthResponseError) as e:
        session.get_token_info(True)

    assert e.value.status_code == 503
    assert client._session_store.get(DID) is not None

    del server.forced_responses['/oauth/token']
    assert session.get_token_info(True).sub == DID


def test_corrupt_stored_session_is_deleted(server: FakeServer) -> None:
    store: MemoryStore[t.Any] = MemoryStore()
    client = make_client(server, session_store=store)
    login(client, server)

    store.set(DID, {'token_set': {}})
    with pytest.raises(TokenRefreshError, match='invalid'):
        client.restore(DID)

    assert store.get(DID) is None

    login(client, server)
    store.set(BOB_DID, store.get(DID))
    with pytest.raises(TokenRefreshError, match='another account'):
        client.restore(BOB_DID)

    assert store.get(BOB_DID) is None


def test_revoke(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client = make_client(server, on_session_deleted=record_causes(deleted))
    session = login(client, server).session
    token = get_stored_session(client._session_store).token_set.access_token

    session.sign_out()

    assert server.revoked_tokens == [token]
    assert client._session_store.get(DID) is None
    assert isinstance(deleted[0], TokenRevokedError)

    # no session, nothing to do
    client.revoke(DID)
    assert len(server.revoked_tokens) == 1


def test_revoke_deletes_the_session_even_when_the_server_is_down(server: FakeServer) -> None:
    client = make_client(server)
    login(client, server)

    server.forced_responses['/oauth/revoke'] = httpx.Response(500)
    client.revoke(DID)
    assert client._session_store.get(DID) is None


def test_failure_to_store_the_session_revokes_the_tokens(server: FakeServer) -> None:
    class BrokenStore(MemoryStore[OAuthSessionData]):
        @te.override
        def set(self, key: str, value: OAuthSessionData) -> None:
            raise RuntimeError('disk full')

    client = make_client(server, session_store=BrokenStore())

    with pytest.raises(RuntimeError, match='disk full'):
        login(client, server)

    assert len(server.revoked_tokens) == 1
    assert server.revoked_tokens[0].startswith('refresh-')


def test_handle_must_be_claimed_by_the_did_document(server: FakeServer) -> None:
    client = make_client(server)

    server.handle_aliases['impostor.test'] = DID

    with pytest.raises(OAuthResolverError, match='does not include the handle'):
        client.authorize('impostor.test')

    with pytest.raises(OAuthResolverError, match='Failed to resolve identity'):
        client.authorize(UNKNOWN_DID)

    with pytest.raises(OAuthResolverError, match='does not resolve'):
        client.authorize('nobody.test')


@pytest.mark.parametrize(
    ('overrides', 'message'),
    [
        ({'issuer': 'https://evil.test'}, 'must match the requested issuer'),
        ({'require_pushed_authorization_requests': False}, 'require_pushed_authorization_requests'),
        ({'dpop_signing_alg_values_supported': ['ES256K']}, 'dpop_signing_alg_values_supported'),
        ({'token_endpoint_auth_methods_supported': ['none']}, 'private_key_jwt'),
        ({'client_id_metadata_document_supported': False}, 'client_id_metadata_document_supported'),
        ({'authorization_response_iss_parameter_supported': False}, 'iss_parameter'),
        ({'scopes_supported': []}, 'scopes_supported'),
        ({'token_endpoint': 'http://auth.test/token'}, 'token_endpoint'),
        ({'pushed_authorization_request_endpoint': None}, 'pushed_authorization_request_endpoint'),
        ({'require_request_uri_registration': False}, 'require_request_uri_registration'),
    ],
)
def test_authorization_server_metadata_is_validated(
    server: FakeServer, overrides: t.Dict[str, t.Any], message: str
) -> None:
    server.server_metadata_overrides = overrides
    client = make_client(server)

    with pytest.raises(UnsupportedAuthServerError, match=message):
        client.authorize(HANDLE)

    assert server.count('/oauth/par') == 0


@pytest.mark.parametrize(
    ('overrides', 'message'),
    [
        ({'resource': 'https://evil.test'}, 'another resource'),
        ({'authorization_servers': [ISSUER, 'https://evil.test']}, 'exactly one'),
        ({'authorization_servers': []}, 'exactly one'),
        ({'authorization_servers': [f'{ISSUER}/path']}, 'not an origin'),
    ],
)
def test_protected_resource_metadata_is_validated(
    server: FakeServer, overrides: t.Dict[str, t.Any], message: str
) -> None:
    server.resource_metadata_overrides = overrides
    client = make_client(server)

    with pytest.raises(OAuthResolverError, match=message):
        client.authorize(HANDLE)


def test_pds_not_listed_by_the_authorization_server_is_rejected(server: FakeServer) -> None:
    server.server_metadata_overrides = {'protected_resources': ['https://other-pds.test']}

    with pytest.raises(OAuthResolverError, match='not protected by'):
        make_client(server).authorize(HANDLE)


def test_private_pds_url_is_never_requested(server: FakeServer) -> None:
    server.accounts[DID].pds = 'https://169.254.169.254'
    client = make_client(server)

    with pytest.raises(UnsafeUrlError):
        client.authorize(HANDLE)

    assert server.requests == []


def test_redirects_are_not_followed(server: FakeServer) -> None:
    server.forced_responses['/.well-known/oauth-protected-resource'] = httpx.Response(
        302, headers={'Location': 'https://evil.test/'}
    )

    with pytest.raises(OAuthResolverError, match='Unexpected status code 302'):
        make_client(server).authorize(HANDLE)

    assert len(server.requests) == 1


def test_transport_failure_is_reported(server: FakeServer) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError('boom', request=request)

    client = OAuthClient.loopback(
        REDIRECT_URI, SCOPE, transport=httpx.MockTransport(handler), id_resolver=FakeIdResolver(server)
    )
    with pytest.raises(OAuthRequestError, match='boom'):
        client.authorize(HANDLE)


def test_concurrent_restores_refresh_once(server: FakeServer) -> None:
    client = make_client(server)
    login(client, server)
    server.expires_in = 3600

    # make the stored tokens stale
    stale = make_stale(get_stored_session(client._session_store))
    client._session_store.set(DID, stale)

    errors: t.List[BaseException] = []

    def worker() -> None:
        try:
            client.restore(DID)
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert errors == []
    assert server.count('/oauth/token') == 2
    assert len(client._locks) == 0


def test_external_lock_wraps_refresh(server: FakeServer) -> None:
    held: t.List[str] = []

    @contextlib.contextmanager
    def lock(did: str) -> t.Generator[None, None, None]:
        held.append(f'enter:{did}')
        yield
        held.append(f'exit:{did}')

    client = make_client(server, lock=lock)
    login(client, server)
    held.clear()

    client.restore(DID, refresh=True)
    assert held == [f'enter:{DID}', f'exit:{DID}']


def test_failed_authorization_request_leaves_no_state(server: FakeServer) -> None:
    states: MemoryStore[OAuthStateData] = MemoryStore()
    client = make_client(server, state_store=states)
    server.forced_responses['/oauth/par'] = httpx.Response(400, json={'error': 'invalid_request'})

    with pytest.raises(OAuthResponseError) as e:
        client.authorize(HANDLE)

    assert e.value.error == 'invalid_request'
    assert states._values == {}


def test_refreshed_tokens_of_another_account_are_revoked(server: FakeServer) -> None:
    client = make_client(server)
    session = login(client, server).session
    server.token_response_overrides = {'sub': BOB_DID}

    with pytest.raises(TokenRefreshError, match='another account'):
        session.get_token_info(True)

    assert client._session_store.get(DID) is None
    assert len(server.revoked_tokens) == 1
    assert server.revoked_tokens[0].startswith('refresh-')


def test_identifier_can_not_choose_the_url_of_identity_requests(server: FakeServer) -> None:
    client = make_client(server)

    with pytest.raises(OAuthResolverError, match='Not a handle or a DID'):
        client.authorize('10.0.0.5:8443/admin?x=')

    with pytest.raises(OAuthResolverError, match='Not a supported DID'):
        client.authorize('did:web:internal.host/path?')

    assert server.requests == []
    assert client._resolver._id_resolver.did.calls == []


def test_handle_resolving_to_an_unsafe_did_is_not_resolved_further(server: FakeServer) -> None:
    server.handle_aliases['alias.test'] = 'did:web:169.254.169.254'
    client = make_client(server)

    with pytest.raises(UnsafeUrlError):
        client.authorize('alias.test')

    assert client._resolver._id_resolver.did.calls == []


def test_unsafe_account_in_token_response_is_not_resolved(server: FakeServer) -> None:
    id_resolver = FakeIdResolver(server)
    client = make_client(server, id_resolver=id_resolver)
    server.token_response_overrides = {'sub': 'did:web:10.0.0.5'}

    with pytest.raises(OAuthCallbackError):
        client.callback(server.approve(client.authorize(PDS)))

    assert id_resolver.did.calls == []
    assert len(server.revoked_tokens) == 1


def test_older_session_object_follows_a_new_login(server: FakeServer) -> None:
    client = make_client(server)
    old = login(client, server).session
    new = login(client, server).session

    # the new login replaced the key along with the tokens; the old object must not sign with the old key
    assert old.get_token_info().sub == DID
    assert old._key.jwk == new._key.jwk == get_stored_session(client._session_store).dpop_jwk


def test_rejected_session_is_kept_when_someone_else_replaced_the_tokens(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client = make_client(server, on_session_deleted=record_causes(deleted))
    login(client, server)
    rejected = get_stored_session(client._session_store).token_set

    client.restore(DID, refresh=True)
    client._drop_rejected_session(DID, rejected)
    assert client._session_store.get(DID) is not None

    client._drop_rejected_session(DID, get_stored_session(client._session_store).token_set)
    assert client._session_store.get(DID) is None
    assert [type(cause).__name__ for cause in deleted] == ['TokenInvalidError']


def test_every_session_operation_takes_the_external_lock(server: FakeServer) -> None:
    held: t.List[str] = []

    @contextlib.contextmanager
    def lock(did: str) -> t.Generator[None, None, None]:
        held.append(did)
        yield

    client = make_client(server, lock=lock)

    login(client, server)
    assert held == [DID]

    client._drop_rejected_session(DID, get_stored_session(client._session_store).token_set)
    client.revoke(DID)
    assert held == [DID, DID, DID]


def test_tokens_are_revoked_when_the_previous_session_can_not_be_read(server: FakeServer) -> None:
    class UnreadableStore(MemoryStore[OAuthSessionData]):
        @te.override
        def get(self, key: str) -> t.Optional[OAuthSessionData]:
            raise RuntimeError('database is down')

    client = make_client(server, session_store=UnreadableStore())

    with pytest.raises(RuntimeError, match='database is down'):
        login(client, server)

    assert len(server.revoked_tokens) == 1


def test_failing_update_callback_does_not_lose_the_session(server: FakeServer) -> None:
    def on_updated(did: str, data: OAuthSessionData) -> None:
        raise RuntimeError('callback failed')

    client = make_client(server, on_session_updated=on_updated)

    with pytest.raises(RuntimeError, match='callback failed'):
        login(client, server)

    assert client._session_store.get(DID) is not None
    assert server.revoked_tokens == []


def test_previous_session_is_kept_when_it_can_not_be_read(server: FakeServer) -> None:
    fail = {'now': False}
    operations: t.List[str] = []

    class FlakyStore(MemoryStore[OAuthSessionData]):
        @te.override
        def get(self, key: str) -> t.Optional[OAuthSessionData]:
            operations.append('get')
            if fail['now']:
                raise RuntimeError('database is down')

            return super().get(key)

        @te.override
        def delete(self, key: str) -> None:
            operations.append('delete')
            super().delete(key)

    client = make_client(server, session_store=FlakyStore())
    login(client, server)
    first_token = get_stored_session(client._session_store).token_set.access_token
    operations.clear()
    fail['now'] = True

    with pytest.raises(RuntimeError, match='database is down'):
        login(client, server)

    fail['now'] = False
    assert operations == ['get']
    assert get_stored_session(client._session_store).token_set.access_token == first_token
    assert len(server.revoked_tokens) == 1
    assert server.revoked_tokens[0] != first_token


def test_refreshed_tokens_are_revoked_when_they_can_not_be_stored(server: FakeServer) -> None:
    fail = {'now': False}

    class FlakyStore(MemoryStore[OAuthSessionData]):
        @te.override
        def set(self, key: str, value: OAuthSessionData) -> None:
            if fail['now']:
                raise RuntimeError('disk full')

            super().set(key, value)

    deleted: t.List[BaseException] = []
    client = make_client(server, session_store=FlakyStore(), on_session_deleted=record_causes(deleted))
    session = login(client, server).session
    fail['now'] = True

    with pytest.raises(RuntimeError, match='disk full'):
        session.get_token_info(True)

    assert client._session_store.get(DID) is None
    assert len(server.revoked_tokens) == 1
    assert [str(cause) for cause in deleted] == ['disk full']


def test_stored_session_with_a_broken_key_is_deleted(server: FakeServer) -> None:
    store: MemoryStore[t.Any] = MemoryStore()
    client = make_client(server, session_store=store)
    login(client, server)

    data = get_stored_session(store).to_dict()
    data['dpop_jwk'] = {'kty': 'EC', 'crv': 'P-256', 'x': 'AA', 'y': 'AA', 'd': 'AA'}
    store.set(DID, data)

    with pytest.raises(TokenRefreshError, match='invalid'):
        client.restore(DID)

    assert store.get(DID) is None


def test_deeply_nested_response_is_an_ordinary_error(server: FakeServer) -> None:
    server.forced_responses['/.well-known/oauth-authorization-server'] = httpx.Response(
        200, content=b'[' * 100_000, headers={'Content-Type': 'application/json'}
    )

    with pytest.raises(UnsupportedAuthServerError):
        make_client(server).authorize(HANDLE)


def test_abandoned_authorizations_are_bounded(server: FakeServer, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('atproto_oauth.client.DEFAULT_MAX_PENDING_AUTHORIZATIONS', 3)
    client = make_client(server)

    urls = [client.authorize(HANDLE) for _ in range(5)]

    assert len(client._state_store._values) == 3
    with pytest.raises(OAuthCallbackError, match='Unknown authorization request'):
        client.callback(server.approve(urls[0]))

    assert client.callback(server.approve(urls[-1])).session.did == DID


def test_stored_authorization_request_with_a_broken_key_is_a_callback_error(server: FakeServer) -> None:
    states: MemoryStore[t.Any] = MemoryStore()
    client = make_client(server, state_store=states)
    params = server.approve(client.authorize(HANDLE))

    stored = states.get(params['state'])
    assert isinstance(stored, OAuthStateData)
    data = stored.to_dict()
    data['dpop_jwk'] = {'kty': 'EC', 'crv': 'P-256', 'x': 'AA', 'y': 'AA', 'd': 'AA'}
    states.set(params['state'], data)

    with pytest.raises(OAuthCallbackError, match='invalid'):
        client.callback(params)
