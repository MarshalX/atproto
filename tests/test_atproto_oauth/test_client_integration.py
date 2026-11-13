import asyncio
import dataclasses
import socketserver
import threading
import typing as t
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
import pytest
import typing_extensions as te
from atproto_client import AsyncClient, Client, models
from atproto_client.exceptions import RequestException, UnauthorizedError
from atproto_client.models.common import XrpcError
from atproto_client.request import AsyncRequest, Request
from atproto_core.exceptions import AtProtocolError
from atproto_oauth import AsyncOAuthClient, OAuthClient
from atproto_oauth.exceptions import TokenInvalidError, TokenRefreshError, TokenRevokedError

from tests.test_atproto_oauth.fake_server import (
    DID,
    HANDLE,
    PDS,
    FakeServer,
    async_fake_id_resolver,
    decode_jwt,
    fake_id_resolver,
    get_stored_session,
    record_causes,
)

SCOPE = 'atproto transition:generic'
PROFILE = models.AppBskyActorGetProfile.Params(actor=HANDLE)
PROFILE_PATH = '/xrpc/app.bsky.actor.getProfile'


class _LocalServer(HTTPServer):
    @te.override
    def server_bind(self) -> None:
        # the base class also looks up the name of the host, which takes seconds on some systems
        socketserver.TCPServer.server_bind(self)
        self.server_port = self.server_address[1]


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


def make_sync(server: FakeServer, **kwargs: t.Any) -> t.Tuple[Client, OAuthClient]:
    oauth = OAuthClient.loopback(
        scope=SCOPE, transport=server.transport, id_resolver=fake_id_resolver(server), **kwargs
    )
    session = oauth.callback(server.approve(oauth.authorize(HANDLE))).session

    client = Client(request=Request(transport=server.transport))
    client.login_oauth(session)
    return client, oauth


async def make_async(server: FakeServer, **kwargs: t.Any) -> t.Tuple[AsyncClient, AsyncOAuthClient]:
    oauth = AsyncOAuthClient.loopback(
        scope=SCOPE, transport=server.transport, id_resolver=async_fake_id_resolver(server), **kwargs
    )
    session = (await oauth.callback(server.approve(await oauth.authorize(HANDLE)))).session

    client = AsyncClient(request=AsyncRequest(transport=server.transport))
    await client.login_oauth(session)
    return client, oauth


def test_requests_go_to_the_pds_of_the_account_with_dpop(server: FakeServer) -> None:
    client, _ = make_sync(server)
    assert client.me is None

    profile = client.app.bsky.actor.get_profile(PROFILE)
    assert profile.did == DID

    # the nonce of the PDS is learned on the first request, within the same call
    assert server.statuses(PROFILE_PATH) == [401, 200]

    request = server.requests[-1]
    assert str(request.url).startswith(f'{PDS}/xrpc/app.bsky.actor.getProfile?actor=')
    assert request.headers['authorization'].startswith('DPoP access-')
    _, payload = decode_jwt(request.headers['dpop'])
    assert payload['htu'] == f'{PDS}/xrpc/app.bsky.actor.getProfile'
    assert payload['htm'] == 'GET'
    assert payload['nonce'] == server.pds_nonce

    client.app.bsky.actor.get_profile(PROFILE)
    assert server.statuses(PROFILE_PATH) == [401, 200, 200]


def test_nonce_rotation_is_invisible(server: FakeServer) -> None:
    client, _ = make_sync(server)
    client.app.bsky.actor.get_profile(PROFILE)

    server.pds_nonce = 'pds-nonce-2'
    client.app.bsky.actor.get_profile(PROFILE)
    assert server.statuses(PROFILE_PATH) == [401, 200, 401, 200]


def test_expired_token_is_refreshed_and_the_request_repeated(server: FakeServer) -> None:
    client, _ = make_sync(server)
    client.app.bsky.actor.get_profile(PROFILE)

    server.expire_access_tokens()
    assert client.app.bsky.actor.get_profile(PROFILE).did == DID

    assert server.statuses(PROFILE_PATH) == [401, 200, 401, 200]
    assert server.count('/oauth/token') == 2


def test_stale_token_is_refreshed_before_the_request(server: FakeServer) -> None:
    server.expires_in = 5
    client, _ = make_sync(server)
    server.expires_in = 3600

    client.app.bsky.actor.get_profile(PROFILE)
    assert server.count('/oauth/token') == 2
    assert server.statuses(PROFILE_PATH) == [401, 200]


def test_session_rejected_after_refresh_is_deleted(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client, oauth = make_sync(server, on_session_deleted=record_causes(deleted))
    client.app.bsky.actor.get_profile(PROFILE)

    # the PDS rejects every token, including freshly issued ones
    server.reject_new_access_tokens = True
    server.expire_access_tokens()

    with pytest.raises(UnauthorizedError) as e:
        client.app.bsky.actor.get_profile(PROFILE)

    assert e.value.response is not None
    assert isinstance(e.value.response.content, XrpcError)
    assert e.value.response.content.error == 'invalid_token'
    assert isinstance(deleted[0], TokenInvalidError)
    assert oauth._session_store.get(DID) is None


def test_request_fails_as_unauthorized_when_refresh_is_impossible(server: FakeServer) -> None:
    client, oauth = make_sync(server)
    client.app.bsky.actor.get_profile(PROFILE)

    server.expire_access_tokens()
    server.grants[-1].revoked = True

    with pytest.raises(UnauthorizedError):
        client.app.bsky.actor.get_profile(PROFILE)

    assert oauth._session_store.get(DID) is None


def test_blob_body_is_repeated_intact(server: FakeServer) -> None:
    client, _ = make_sync(server)
    payload = bytes(range(256)) * 16

    server.forced_responses.clear()
    response = client.request.post(
        f'{PDS}/xrpc/com.example.upload', content=payload, headers={'Content-Type': 'image/png'}
    )

    assert server.statuses('/xrpc/com.example.upload') == [401, 200]
    assert server.bodies[-1] == payload
    assert isinstance(response.content, dict)
    assert response.content['size'] == len(payload)


def test_send_post_works_without_a_profile(server: FakeServer) -> None:
    client, _ = make_sync(server)

    post = client.send_post('Hello from OAuth')

    assert post.uri == f'at://{DID}/app.bsky.feed.post/3kabc'


def test_profile_can_be_fetched_on_login(server: FakeServer) -> None:
    oauth = OAuthClient.loopback(scope=SCOPE, transport=server.transport, id_resolver=fake_id_resolver(server))
    session = oauth.callback(server.approve(oauth.authorize(HANDLE))).session

    client = Client(request=Request(transport=server.transport))
    profile = client.login_oauth(session, fetch_bsky_profile=True)

    assert profile is not None
    assert client.me is profile
    assert profile.did == DID


def test_explicit_authorization_header_is_left_alone(server: FakeServer) -> None:
    client, _ = make_sync(server)

    client.request.get(f'{PDS}/xrpc/com.example.echo', headers={'Authorization': 'Bearer service-token'})

    request = server.requests[-1]
    assert request.headers['authorization'] == 'Bearer service-token'
    assert 'dpop' not in request.headers
    assert server.statuses('/xrpc/com.example.echo') == [200]


def test_clones_share_the_session(server: FakeServer) -> None:
    oauth = OAuthClient.loopback(scope=SCOPE, transport=server.transport, id_resolver=fake_id_resolver(server))
    session = oauth.callback(server.approve(oauth.authorize(HANDLE))).session

    client = Client(request=Request(transport=server.transport))
    early_clone = client.clone()
    client.login_oauth(session)
    late_clone = client.with_bsky_chat_proxy()

    assert early_clone.app.bsky.actor.get_profile(PROFILE).did == DID
    assert late_clone.app.bsky.actor.get_profile(PROFILE).did == DID
    assert server.requests[-1].headers['atproto-proxy'].startswith('did:web:api.bsky.chat')

    # the session is gone for every clone: back to the default host, unauthenticated
    client.logout_oauth()
    with pytest.raises(RequestException):
        early_clone.app.bsky.actor.get_profile(PROFILE)

    assert server.requests[-1].url.host == 'bsky.social'
    assert 'authorization' not in server.requests[-1].headers


def test_base_url_follows_the_session(server: FakeServer) -> None:
    client, _ = make_sync(server)
    assert client._build_url('com.example.echo') == f'{PDS}/xrpc/com.example.echo'

    client.logout_oauth()
    assert client._build_url('com.example.echo') == 'https://bsky.social/xrpc/com.example.echo'
    assert client.me is None


def test_session_string_can_not_be_exported(server: FakeServer) -> None:
    client, _ = make_sync(server)

    with pytest.raises(AtProtocolError, match='session store'):
        client.export_session_string()


def test_session_change_callbacks_are_not_called(server: FakeServer) -> None:
    oauth = OAuthClient.loopback(scope=SCOPE, transport=server.transport, id_resolver=fake_id_resolver(server))
    session = oauth.callback(server.approve(oauth.authorize(HANDLE))).session

    events: t.List[t.Any] = []
    client = Client(request=Request(transport=server.transport))
    client.on_session_change(lambda event, session: events.append(event))
    client.login_oauth(session)

    server.expire_access_tokens()
    client.app.bsky.actor.get_profile(PROFILE)
    assert events == []


def test_signed_out_session_raises(server: FakeServer) -> None:
    client, oauth = make_sync(server)
    oauth.revoke(DID)

    with pytest.raises(TokenRefreshError):
        client.app.bsky.actor.get_profile(PROFILE)


def test_session_of_the_wrong_kind_is_rejected(server: FakeServer) -> None:
    _, oauth = make_sync(server)
    sync_session = oauth.restore(DID)

    async def run() -> None:
        client = AsyncClient(request=AsyncRequest(transport=server.transport))
        await client.login_oauth(sync_session)
        with pytest.raises(RuntimeError, match='AsyncOAuthSession'):
            await client.app.bsky.actor.get_profile(PROFILE)

    asyncio.run(run())


def test_concurrent_requests_refresh_once(server: FakeServer) -> None:
    client, _ = make_sync(server)
    client.app.bsky.actor.get_profile(PROFILE)
    server.expire_access_tokens()

    errors: t.List[BaseException] = []

    def worker() -> None:
        try:
            client.app.bsky.actor.get_profile(PROFILE)
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert errors == []
    assert server.count('/oauth/token') == 2


def test_streamed_body_is_buffered_for_the_retry() -> None:
    """Needs a real transport: ``MockTransport`` does not consume a streamed body."""
    received: t.List[bytes] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            received.append(self._read_chunked())
            first = len(received) == 1
            self.send_response(401 if first else 200)
            if first:
                self.send_header('WWW-Authenticate', 'DPoP error="use_dpop_nonce"')

            self.send_header('DPoP-Nonce', 'nonce-1')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'{}')

        def _read_chunked(self) -> bytes:
            body = b''
            while True:
                size = int(self.rfile.readline().strip(), 16)
                body += self.rfile.read(size)
                self.rfile.readline()
                if not size:
                    return body

        @te.override
        def log_message(self, format: str, *args: t.Any) -> None:
            pass

    fake = FakeServer()
    http_server = _LocalServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=http_server.serve_forever, daemon=True).start()
    try:
        oauth = OAuthClient.loopback(scope=SCOPE, transport=fake.transport, id_resolver=fake_id_resolver(fake))
        oauth.callback(fake.approve(oauth.authorize(HANDLE)))

        # the session only signs requests to the PDS of the account, so the local server is made that PDS
        data = get_stored_session(oauth._session_store)
        local_pds = f'http://127.0.0.1:{http_server.server_port}'
        local_data = dataclasses.replace(data, token_set=dataclasses.replace(data.token_set, aud=local_pds))
        oauth._session_store.set(DID, local_data)
        session = oauth.restore(DID, refresh=False)

        def chunks() -> t.Iterator[bytes]:
            yield b'chunk-1'
            yield b'chunk-2'

        with httpx.Client() as http:
            response = http.post(
                f'http://127.0.0.1:{http_server.server_port}/xrpc/com.example.upload',
                content=chunks(),
                auth=session.httpx_auth,
            )

        assert response.status_code == 200
        assert received == [b'chunk-1chunk-2', b'chunk-1chunk-2']
    finally:
        http_server.shutdown()
        http_server.server_close()


@pytest.mark.asyncio
async def test_async_requests_with_dpop_refresh_and_nonce(server: FakeServer) -> None:
    client, _ = await make_async(server)

    assert (await client.app.bsky.actor.get_profile(PROFILE)).did == DID
    assert server.statuses(PROFILE_PATH) == [401, 200]

    server.pds_nonce = 'pds-nonce-2'
    server.expire_access_tokens()
    assert (await client.app.bsky.actor.get_profile(PROFILE)).did == DID
    assert server.statuses(PROFILE_PATH) == [401, 200, 401, 401, 200]
    assert server.count('/oauth/token') == 2

    post = await client.send_post('Hello from OAuth')
    assert post.uri == f'at://{DID}/app.bsky.feed.post/3kabc'


@pytest.mark.asyncio
async def test_async_session_rejected_after_refresh_is_deleted(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []

    async def on_deleted(did: str, cause: BaseException) -> None:
        deleted.append(cause)

    client, oauth = await make_async(server, on_session_deleted=on_deleted)
    await client.app.bsky.actor.get_profile(PROFILE)

    server.reject_new_access_tokens = True
    server.expire_access_tokens()

    with pytest.raises(UnauthorizedError):
        await client.app.bsky.actor.get_profile(PROFILE)

    assert isinstance(deleted[0], TokenInvalidError)
    assert oauth._session_store.get(DID) is None


@pytest.mark.asyncio
async def test_async_concurrent_requests_refresh_once(server: FakeServer) -> None:
    client, oauth = await make_async(server)
    await client.app.bsky.actor.get_profile(PROFILE)
    server.expire_access_tokens()

    results = await asyncio.gather(
        *[client.app.bsky.actor.get_profile(PROFILE) for _ in range(16)], return_exceptions=True
    )

    assert [r for r in results if isinstance(r, BaseException)] == []
    assert server.count('/oauth/token') == 2
    assert len(oauth._locks) == 0


@pytest.mark.asyncio
async def test_async_session_revoke(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    _, oauth = await make_async(server, on_session_deleted=record_causes(deleted))
    session = await oauth.restore(DID)

    await session.revoke()

    assert isinstance(deleted[0], TokenRevokedError)
    assert len(server.revoked_tokens) == 1


def test_tokens_are_not_sent_to_other_hosts(server: FakeServer) -> None:
    client, _ = make_sync(server)
    seen: t.List[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={})

    auth = client._session_dispatcher.get_httpx_auth()
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        for url in ('https://elsewhere.test/xrpc/x', 'http://pds.test/xrpc/x', 'https://pds.test:8443/xrpc/x'):
            http.get(url, auth=auth)

    assert len(seen) == 3
    for request in seen:
        assert 'authorization' not in request.headers
        assert 'dpop' not in request.headers


def test_older_session_keeps_working_after_a_new_login(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client, oauth = make_sync(server, on_session_deleted=record_causes(deleted))
    oauth.callback(server.approve(oauth.authorize(HANDLE)))
    deleted.clear()

    # the client still holds the session object of the first login
    assert client.app.bsky.actor.get_profile(PROFILE).did == DID

    server.expire_access_tokens()
    assert client.app.bsky.actor.get_profile(PROFILE).did == DID
    assert deleted == []
    assert oauth._session_store.get(DID) is not None


@pytest.mark.asyncio
async def test_async_older_session_keeps_working_after_a_new_login(server: FakeServer) -> None:
    deleted: t.List[BaseException] = []
    client, oauth = await make_async(server, on_session_deleted=record_causes(deleted))
    await oauth.callback(server.approve(await oauth.authorize(HANDLE)))
    deleted.clear()

    assert (await client.app.bsky.actor.get_profile(PROFILE)).did == DID
    assert deleted == []
    assert oauth._session_store.get(DID) is not None
