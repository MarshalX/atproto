"""Tests for the OAuth SSRF guard."""

import httpx
import pytest
from atproto_oauth.security import (
    UnsafeUrlError,
    get_hardened_async_client,
    get_hardened_client,
    is_safe_url,
)


class TestIsSafeUrl:
    @pytest.mark.parametrize(
        'url',
        [
            'https://bsky.social',
            'https://pds.example.com/xrpc/com.atproto.sync.getBlob',
            'https://example.com:8443/path?query=1',
            'https://8.8.8.8',
        ],
    )
    def test_allows_ordinary_public_urls(self, url: str) -> None:
        assert is_safe_url(url) is True

    @pytest.mark.parametrize(
        'url',
        [
            'http://example.com',  # cleartext to a non-local host
            'file:///etc/passwd',
            'ftp://example.com',
            'gopher://example.com',
            'https://',  # no host
        ],
    )
    def test_rejects_by_scheme_or_missing_host(self, url: str) -> None:
        assert is_safe_url(url) is False

    @pytest.mark.parametrize(
        'url',
        [
            'https://10.0.0.1',
            'https://172.16.0.1',
            'https://172.31.255.255',
            'https://192.168.1.1',
            'https://127.0.0.1',
            'https://0.0.0.0',
            'https://169.254.169.254',  # AWS/Azure metadata
            'https://169.254.1.1',  # the rest of link-local, not just metadata
            'https://100.64.0.1',  # CGNAT / tailscale
            'https://metadata.google.internal',
            'https://[::1]',
            'https://[fc00::1]',  # IPv6 unique-local
            'https://[fe80::1]',  # IPv6 link-local
            'https://224.0.0.1',  # multicast
        ],
    )
    def test_rejects_addresses_that_must_not_be_reached(self, url: str) -> None:
        assert is_safe_url(url) is False

    @pytest.mark.parametrize(
        'url',
        [
            'https://2130706433',  # 127.0.0.1 as a bare integer
            'https://[::ffff:127.0.0.1]',  # IPv4-mapped loopback
            'https://[::ffff:169.254.169.254]',  # IPv4-mapped metadata
            'https://0177.0.0.1',  # octal, rejected as address-shaped
            'https://127.1',  # short form, rejected as address-shaped
            'https://192.168.1',
        ],
    )
    def test_rejects_alternate_address_notations(self, url: str) -> None:
        """These all reach a private address through the OS resolver."""
        assert is_safe_url(url) is False

    def test_hostname_beginning_with_digits_is_still_a_name(self) -> None:
        """`10.example.com` is a DNS name, not 10.0.0.0/8."""
        assert is_safe_url('https://10.example.com') is True
        assert is_safe_url('https://192.168.example.com') is True

    @pytest.mark.parametrize('host', ['localhost', '127.0.0.1', '[::1]'])
    def test_allow_localhost_permits_only_localhost(self, host: str) -> None:
        assert is_safe_url(f'http://{host}:3000', allow_localhost=True) is True
        assert is_safe_url(f'https://{host}', allow_localhost=True) is True

    def test_allow_localhost_does_not_unlock_the_rest_of_the_private_space(self) -> None:
        """The escape hatch is for local development, not for 10/8."""
        assert is_safe_url('https://10.0.0.1', allow_localhost=True) is False
        assert is_safe_url('https://169.254.169.254', allow_localhost=True) is False
        assert is_safe_url('http://10.0.0.1', allow_localhost=True) is False

    def test_rejects_garbage_rather_than_raising(self) -> None:
        for value in ['', 'not a url', '://', 'https://[oops']:
            assert is_safe_url(value) is False


class TestHardenedClientRedirects:
    """A validated URL can still 302 to somewhere it must not go."""

    def test_sync_client_refuses_a_redirect_to_a_private_address(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == 'example.com':
                return httpx.Response(302, headers={'Location': 'https://169.254.169.254/latest/meta-data/'})
            return httpx.Response(200, text='should never be reached')

        client = get_hardened_client()
        client._transport._inner = httpx.MockTransport(handler)

        with pytest.raises(UnsafeUrlError):
            client.get('https://example.com')

    @pytest.mark.asyncio
    async def test_async_client_refuses_a_redirect_to_a_private_address(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == 'example.com':
                return httpx.Response(302, headers={'Location': 'http://127.0.0.1:6379/'})
            return httpx.Response(200, text='should never be reached')

        client = get_hardened_async_client()
        client._transport._inner = httpx.MockTransport(handler)

        with pytest.raises(UnsafeUrlError):
            await client.get('https://example.com')

    def test_sync_client_follows_a_safe_redirect(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == 'example.com':
                return httpx.Response(302, headers={'Location': 'https://cdn.example.org/blob'})
            return httpx.Response(200, text='ok')

        client = get_hardened_client()
        client._transport._inner = httpx.MockTransport(handler)

        response = client.get('https://example.com')
        assert response.status_code == 200
        assert response.text == 'ok'
