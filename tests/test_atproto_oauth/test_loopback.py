import asyncio
import typing as t
import urllib.error
import urllib.request
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest
from atproto_oauth import AsyncOAuthClient, OAuthClient
from atproto_oauth.exceptions import OAuthCallbackError
from atproto_oauth.loopback import LoopbackCallbackServer

from tests.test_atproto_oauth.fake_server import DID, HANDLE, FakeServer, async_fake_id_resolver, fake_id_resolver

SCOPE = 'atproto transition:generic'


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


def make_client(server: FakeServer, **kwargs: t.Any) -> OAuthClient:
    return OAuthClient.loopback(scope=SCOPE, transport=server.transport, id_resolver=fake_id_resolver(server), **kwargs)


def make_async_client(server: FakeServer) -> AsyncOAuthClient:
    return AsyncOAuthClient.loopback(
        scope=SCOPE, transport=server.transport, id_resolver=async_fake_id_resolver(server)
    )


def get(url: str) -> int:
    try:
        with urllib.request.urlopen(url) as response:  # noqa: S310
            return int(response.status)
    except urllib.error.HTTPError as e:
        return e.code


def browser(server: FakeServer, redirects: t.List[str], deny: bool = False) -> t.Callable[[str], None]:
    """Act as the browser: the user decides and the authorization server redirects back."""

    def open_url(url: str) -> None:
        query = dict(parse_qsl(urlsplit(url).query))
        redirect_uri = server.par_requests[query['request_uri']]['redirect_uri']
        redirects.append(redirect_uri)

        params = server.deny(url) if deny else server.approve(url)
        assert get(f'{redirect_uri}?{urlencode(params)}') == 200

    return open_url


def test_login_with_browser(server: FakeServer) -> None:
    client = make_client(server)
    redirects: t.List[str] = []

    session = client.login_with_browser(HANDLE, open_url=browser(server, redirects), scope='atproto')

    assert session.did == DID
    assert session.get_token_info().scope == 'atproto'
    assert client.restore(DID).did == DID

    redirect = urlsplit(redirects[0])
    assert redirect.hostname == '127.0.0.1'
    assert redirect.port
    assert redirect.path == '/'

    with pytest.raises(urllib.error.URLError):
        get(redirects[0])


@pytest.mark.asyncio
async def test_login_with_browser_async(server: FakeServer) -> None:
    client = make_async_client(server)
    redirects: t.List[str] = []

    session = await client.login_with_browser(HANDLE, open_url=browser(server, redirects))

    assert session.did == DID
    assert (await client.restore(DID)).did == DID

    with pytest.raises(urllib.error.URLError):
        get(redirects[0])


def test_login_with_browser_reports_denial(server: FakeServer) -> None:
    client = make_client(server)

    with pytest.raises(OAuthCallbackError, match='denied') as e:
        client.login_with_browser(HANDLE, open_url=browser(server, [], deny=True))

    assert e.value.error == 'access_denied'


def test_login_with_browser_times_out(server: FakeServer) -> None:
    client = make_client(server)
    urls: t.List[str] = []

    with pytest.raises(OAuthCallbackError, match='not completed in time'):
        client.login_with_browser(HANDLE, open_url=urls.append, timeout=0.01)

    assert len(urls) == 1


@pytest.mark.asyncio
async def test_login_with_browser_can_be_cancelled(server: FakeServer) -> None:
    client = make_async_client(server)
    opened = asyncio.Event()

    task = asyncio.ensure_future(client.login_with_browser(HANDLE, open_url=lambda _: opened.set(), timeout=None))
    await opened.wait()
    await asyncio.sleep(0.05)

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_login_with_browser_needs_a_loopback_redirect_uri(server: FakeServer) -> None:
    client = OAuthClient.public(
        'https://app.test/client-metadata.json', 'https://app.test/callback', SCOPE, transport=server.transport
    )

    with pytest.raises(ValueError, match='no redirect URI'):
        client.login_with_browser(HANDLE)


def test_callback_server_serves_only_the_registered_path_once() -> None:
    with LoopbackCallbackServer(['https://app.test/callback', 'http://127.0.0.1/callback']) as callback_server:
        base = callback_server.redirect_uri
        assert urlsplit(base).path == '/callback'

        assert get(base.replace('/callback', '/favicon.ico')) == 404
        assert get(f'{base}?code=first&state=s') == 200
        assert get(f'{base}?code=second&state=s') == 404

        assert callback_server.wait(0) == {'code': 'first', 'state': 's'}


def test_callback_server_keeps_a_registered_port_and_ipv6_host() -> None:
    with LoopbackCallbackServer(['http://127.0.0.1/']) as picked:
        port = urlsplit(picked.redirect_uri).port

    with LoopbackCallbackServer([f'http://127.0.0.1:{port}/']) as fixed:
        assert fixed.redirect_uri == f'http://127.0.0.1:{port}/'

    try:
        ipv6 = LoopbackCallbackServer(['http://[::1]/'])
    except OSError:
        pytest.skip('IPv6 loopback is not available')

    with ipv6:
        assert ipv6.redirect_uri.startswith('http://[::1]:')
        assert get(f'{ipv6.redirect_uri}?code=c') == 200


def test_authorize_accepts_a_registered_loopback_redirect_uri_on_any_port(server: FakeServer) -> None:
    client = make_client(server)

    client.authorize(HANDLE, redirect_uri='http://127.0.0.1:50123/')
    client.authorize(HANDLE, redirect_uri='http://[::1]:50123/')

    with pytest.raises(ValueError, match='not registered'):
        client.authorize(HANDLE, redirect_uri='http://127.0.0.1:50123/other')

    public = OAuthClient.public(
        'https://app.test/client-metadata.json', 'https://app.test/callback', SCOPE, transport=server.transport
    )
    with pytest.raises(ValueError, match='not registered'):
        public.authorize(HANDLE, redirect_uri='https://app.test:8443/callback')
