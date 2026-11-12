import asyncio
import typing as t

import httpx
import pytest
import typing_extensions as te
from atproto_oauth.exceptions import OAuthRequestError, OAuthResolverError, UnsafeUrlError
from atproto_oauth.resolver import ensure_safe_identifier
from atproto_oauth.security import (
    MAX_RESPONSE_SIZE,
    AsyncHttpClient,
    HttpClient,
    ensure_safe_url,
    get_origin,
    is_safe_url,
)


@pytest.mark.parametrize(
    'url',
    [
        'https://bsky.social',
        'https://pds.example.com/xrpc/com.atproto.sync.getBlob',
        'https://example.com:8443/path?query=1',
        'https://8.8.8.8',
        'https://10.example.com',
        'https://192.168.example.com',
    ],
)
def test_public_urls_are_allowed(url: str) -> None:
    assert is_safe_url(url)


@pytest.mark.parametrize(
    'url',
    [
        'http://example.com',
        'file:///etc/passwd',
        'ftp://example.com',
        'gopher://example.com',
        'https://',
        '',
        'not a url',
        '://',
        'https://[oops',
        'https://example.com:port',
        'https://user:password@example.com',
    ],
)
def test_other_schemes_and_malformed_urls_are_rejected(url: str) -> None:
    assert not is_safe_url(url)


@pytest.mark.parametrize(
    'url',
    [
        'https://10.0.0.1',
        'https://172.16.0.1',
        'https://172.31.255.255',
        'https://192.168.1.1',
        'https://127.0.0.1',
        'https://0.0.0.0',
        'https://169.254.169.254',
        'https://169.254.1.1',
        'https://100.64.0.1',
        'https://metadata.google.internal',
        'https://localhost',
        'https://LOCALHOST',
        'https://[::1]',
        'https://[fc00::1]',
        'https://[fe80::1]',
        'https://224.0.0.1',
        # other ways to write private addresses
        'https://2130706433',
        'https://[::ffff:127.0.0.1]',
        'https://[::ffff:169.254.169.254]',
        'https://0177.0.0.1',
        'https://127.1',
        'https://192.168.1',
        'https://0x7f000001',
        'https://0x7f.0.0.0x1',
        'https://017700000001',
        'https://[64:ff9b::7f00:1]',
        # names that never leave the machine or the local network
        'https://localhost.',
        'https://metadata.google.internal.',
        'https://foo.localhost',
        'https://printer.local',
        'https://db.internal',
        'https://exa mple.com',
        'https://metadata',
        'https://intranet',
        'https://kubernetes.default.svc',
        'https://router.lan',
        'https://foo.home.arpa',
        'https://[::127.0.0.1]',
        'https://[::a00:1]',
        'https://[::ffff:0:127.0.0.1]',
        'https://[::ffff:0:a00:1]',
        'https://files.corp',
        'https://nas.home',
        'https://localhost.localdomain',
        'https://wiki.intranet',
        'https://db.private',
    ],
)
def test_private_addresses_are_rejected_in_every_notation(url: str) -> None:
    assert not is_safe_url(url)


@pytest.mark.parametrize('host', ['localhost', '127.0.0.1', '[::1]'])
def test_allow_http_permits_loopback(host: str) -> None:
    assert is_safe_url(f'http://{host}:2583', allow_http=True)
    assert is_safe_url(f'https://{host}', allow_http=True)


def test_allow_http_permits_names_without_a_dot() -> None:
    assert is_safe_url('http://pds:2583', allow_http=True)
    assert not is_safe_url('https://pds')


def test_allow_http_does_not_unlock_private_networks() -> None:
    assert is_safe_url('http://pds.example.com', allow_http=True)
    assert not is_safe_url('https://10.0.0.1', allow_http=True)
    assert not is_safe_url('http://10.0.0.1', allow_http=True)
    assert not is_safe_url('http://169.254.169.254', allow_http=True)


def test_ensure_safe_url_raises() -> None:
    ensure_safe_url('https://bsky.social')
    with pytest.raises(UnsafeUrlError):
        ensure_safe_url('https://127.0.0.1')


@pytest.mark.parametrize(
    ('url', 'origin'),
    [
        ('https://bsky.social', 'https://bsky.social'),
        ('https://BSKY.social:443/xrpc/x?y=1#z', 'https://bsky.social'),
        ('https://bsky.social:8443/', 'https://bsky.social:8443'),
        ('http://localhost:2583/xrpc', 'http://localhost:2583'),
        ('http://[::1]:80', 'http://[::1]'),
    ],
)
def test_get_origin(url: str, origin: str) -> None:
    assert get_origin(url) == origin


def test_get_origin_rejects_relative_urls() -> None:
    with pytest.raises(ValueError, match='Not an absolute URL'):
        get_origin('/path')


def test_http_client_checks_urls_and_does_not_follow_redirects() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(302, headers={'Location': 'https://169.254.169.254/latest/meta-data/'})

    client = HttpClient(httpx.MockTransport(handler))

    assert client.request('GET', 'https://example.com').status_code == 302
    assert seen == ['https://example.com']

    with pytest.raises(UnsafeUrlError):
        client.request('GET', 'https://169.254.169.254/latest/meta-data/')

    assert len(seen) == 1


def test_http_client_limits_the_response_size() -> None:
    client = HttpClient(
        httpx.MockTransport(lambda request: httpx.Response(200, content=b'x' * (MAX_RESPONSE_SIZE + 1)))
    )

    with pytest.raises(OAuthRequestError, match='larger than'):
        client.request('GET', 'https://example.com')


def test_http_response_json() -> None:
    client = HttpClient(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200, content=b'<html>', headers={'Content-Type': 'application/json; charset=utf-8'}
            )
        )
    )
    response = client.request('GET', 'https://example.com')

    assert response.is_json
    assert response.json() is None


def test_http_client_reports_an_unusable_url() -> None:
    client = HttpClient(httpx.MockTransport(lambda request: httpx.Response(200)))

    with pytest.raises(UnsafeUrlError):
        client.request('GET', 'https://exa mple.com/')


@pytest.mark.parametrize(
    'identifier',
    [
        'alice.bsky.social',
        '@Alice.Bsky.Social',
        'did:plc:kvwvcn5iqfooopmyzvb4qzba',
        'did:web:example.com',
    ],
)
def test_handles_and_dids_are_safe_to_resolve(identifier: str) -> None:
    ensure_safe_identifier(identifier, allow_http=False)


@pytest.mark.parametrize(
    'identifier',
    [
        '10.0.0.5:8443/admin?x=',
        'example.com/path',
        'example.com:8443',
        'user@example.com',
        'localhost',
        'did:web:internal.host/path?',
        'did:web:example.com%3A8443',
        'did:web:example.com:path',
        'did:plc:short',
        'did:key:zQ3shokFTS3brHcDQrn82RUDfCZESWL1ZdCEJwekUDPQiYBme',
    ],
)
def test_identifiers_that_would_choose_the_request_url_are_rejected(identifier: str) -> None:
    with pytest.raises(OAuthResolverError):
        ensure_safe_identifier(identifier, allow_http=False)


@pytest.mark.parametrize('identifier', ['127.0.0.1', 'printer.local', 'did:web:10.0.0.5', 'did:web:db.internal'])
def test_identifiers_of_private_hosts_are_rejected(identifier: str) -> None:
    with pytest.raises((UnsafeUrlError, OAuthResolverError)):
        ensure_safe_identifier(identifier, allow_http=False)


def test_development_did_web_needs_allow_http() -> None:
    ensure_safe_identifier('did:web:localhost%3A2583', allow_http=True)

    with pytest.raises(OAuthResolverError):
        ensure_safe_identifier('did:web:localhost%3A2583', allow_http=False)


def test_http_client_gives_up_on_a_response_that_keeps_coming(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = iter([0.0, 100.0, 200.0, 300.0])
    monkeypatch.setattr('atproto_oauth.security.time.monotonic', lambda: next(clock))
    client = HttpClient(httpx.MockTransport(lambda request: httpx.Response(200, content=b'slow')), timeout=10)

    with pytest.raises(OAuthRequestError, match='took too long'):
        client.request('GET', 'https://example.com')


class _SlowStream(httpx.AsyncByteStream):
    @te.override
    async def __aiter__(self) -> t.AsyncIterator[bytes]:
        for _ in range(3):
            await asyncio.sleep(0.05)
            yield b'slow'


@pytest.mark.asyncio
async def test_async_http_client_has_the_same_limits() -> None:
    oversized = httpx.Response(200, content=b'x' * (MAX_RESPONSE_SIZE + 1))
    large = AsyncHttpClient(httpx.MockTransport(lambda request: oversized))
    with pytest.raises(OAuthRequestError, match='larger than'):
        await large.request('GET', 'https://example.com')

    with pytest.raises(UnsafeUrlError):
        await large.request('GET', 'https://127.0.0.1')

    slow = AsyncHttpClient(httpx.MockTransport(lambda request: httpx.Response(200, stream=_SlowStream())), timeout=0.01)
    with pytest.raises(OAuthRequestError, match='took too long'):
        await slow.request('GET', 'https://example.com')
