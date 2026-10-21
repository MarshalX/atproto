"""Security utilities for OAuth implementation."""

from __future__ import annotations

import ipaddress
import typing as t
from urllib.parse import urlparse

import httpx

# Hardened HTTP client configuration
DEFAULT_TIMEOUT = 5.0
MAX_REDIRECTS = 3
ALLOWED_SCHEMES = {'https', 'http'}  # http only for localhost
BLOCKED_HOSTS = {
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    '::1',
    '169.254.169.254',  # AWS metadata
    'metadata.google.internal',  # GCP metadata
}
LOCALHOST_HOSTS = {'localhost', '127.0.0.1', '::1'}


class UnsafeUrlError(ValueError):
    """Raised when a request targets a URL that failed :func:`is_safe_url`."""


def _unwrap_ipv6(ip: ipaddress.IPv6Address) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """Resolve IPv6 forms that embed an IPv4 address to that address.

    ``::ffff:127.0.0.1`` reaches the loopback interface, so it must be judged
    as ``127.0.0.1`` rather than as an unremarkable IPv6 address.
    """
    if ip.ipv4_mapped:
        return ip.ipv4_mapped
    if ip.sixtofour:
        return ip.sixtofour
    return ip


def _parse_host_as_ip(hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Parse a hostname as an IP literal, including bare-integer form.

    ``http://2130706433/`` is a valid way to write ``http://127.0.0.1/`` that
    :func:`ipaddress.ip_address` will not parse from a string, so the integer
    form is handled explicitly.
    """
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        pass

    if hostname.isdigit():
        try:
            return ipaddress.ip_address(int(hostname))
        except ValueError:
            return None
    return None


def _looks_like_an_address(hostname: str) -> bool:
    """Whether a hostname is making an address-shaped claim.

    The last label of a real DNS name is never all-digits, so anything ending
    in one is an address written in a form we did not parse -- ``0177.0.0.1``
    and ``127.1`` both reach loopback through the OS resolver while failing
    :func:`ipaddress.ip_address`. Such hosts are rejected rather than treated
    as names.
    """
    last_label = hostname.rstrip('.').rsplit('.', 1)[-1]
    return last_label.isdigit() or ':' in hostname


def _is_forbidden_address(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Whether an address belongs to a range no outbound request should reach."""
    if isinstance(ip, ipaddress.IPv6Address):
        ip = _unwrap_ipv6(ip)
    # `is_global` is the broad criterion: it excludes RFC1918, loopback,
    # link-local (so cloud metadata at 169.254.169.254), unique-local, and
    # CGNAT at 100.64.0.0/10 -- the last of which `is_private` does *not*
    # cover. multicast is checked separately because it is `is_global`.
    return not ip.is_global or ip.is_multicast


def is_safe_url(url: str, allow_localhost: bool = False) -> bool:
    """Validate URL for security (SSRF protection).

    Rejects URLs whose host is an address in a private, loopback, link-local,
    multicast, reserved, or unspecified range, in any notation that reaches
    such an address -- dotted quad, IPv6, IPv4-mapped IPv6, and bare integer.
    Hosts that are shaped like an address but parse as none are rejected too.

    .. warning::
        This inspects the URL only. A hostname that *resolves* to a private
        address still passes, because resolving here would be both a blocking
        call and a time-of-check/time-of-use gap -- the name can resolve
        differently when the connection is actually made. Callers that need
        that guarantee should pin or validate at connection time; the clients
        returned by :func:`get_hardened_client` and
        :func:`get_hardened_async_client` re-check every hop of a redirect
        chain, which closes the redirect half of the problem.

    Args:
        url: URL to validate.
        allow_localhost: Whether to allow localhost URLs.

    Returns:
        True if URL is safe to use.
    """
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # http is cleartext, so it is only ever allowed to reach localhost
        if parsed.scheme == 'http':
            if not allow_localhost:
                return False
            if hostname not in LOCALHOST_HOSTS:
                return False

        if allow_localhost and hostname in LOCALHOST_HOSTS:
            return True

        if hostname in BLOCKED_HOSTS:
            return False

        if (ip := _parse_host_as_ip(hostname)) is not None:
            return not _is_forbidden_address(ip)

        # a host shaped like an address that parsed as none is not a name
        return not _looks_like_an_address(hostname)
    except Exception:
        return False


class _ValidatingTransport(httpx.BaseTransport):
    """Applies :func:`is_safe_url` to every request the client actually sends.

    Validating only the URL a caller passes leaves the redirect hole open: a
    safe host can answer 302 with a ``Location`` pointing at loopback or a
    metadata service, and the client follows it. httpx re-issues each hop
    through the transport, so checking here covers the whole chain.
    """

    def __init__(self, inner: httpx.BaseTransport, allow_localhost: bool) -> None:
        self._inner = inner
        self._allow_localhost = allow_localhost

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if not is_safe_url(str(request.url), self._allow_localhost):
            raise UnsafeUrlError(f'refusing request to {request.url}')
        return self._inner.handle_request(request)

    def close(self) -> None:
        self._inner.close()


class _ValidatingAsyncTransport(httpx.AsyncBaseTransport):
    """Async counterpart to :class:`_ValidatingTransport`."""

    def __init__(self, inner: httpx.AsyncBaseTransport, allow_localhost: bool) -> None:
        self._inner = inner
        self._allow_localhost = allow_localhost

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not is_safe_url(str(request.url), self._allow_localhost):
            raise UnsafeUrlError(f'refusing request to {request.url}')
        return await self._inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self._inner.aclose()


def get_hardened_client(
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = MAX_REDIRECTS,
    allow_localhost: bool = False,
) -> httpx.Client:
    """Create hardened HTTP client with security settings.

    Every request the client sends -- including each redirect hop -- is
    checked with :func:`is_safe_url`, raising :class:`UnsafeUrlError` rather
    than following a redirect to a private address.

    Args:
        timeout: Request timeout in seconds.
        max_redirects: Maximum number of redirects to follow.
        allow_localhost: Whether requests may target localhost.

    Returns:
        Configured httpx.Client.
    """
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        max_redirects=max_redirects,
        # `limits` belongs to the transport, which is supplied below
        transport=_ValidatingTransport(httpx.HTTPTransport(limits=limits), allow_localhost),
    )


def get_hardened_async_client(
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = MAX_REDIRECTS,
    allow_localhost: bool = False,
) -> httpx.AsyncClient:
    """Create hardened async HTTP client with security settings.

    Every request the client sends -- including each redirect hop -- is
    checked with :func:`is_safe_url`, raising :class:`UnsafeUrlError` rather
    than following a redirect to a private address.

    Args:
        timeout: Request timeout in seconds.
        max_redirects: Maximum number of redirects to follow.
        allow_localhost: Whether requests may target localhost.

    Returns:
        Configured httpx.AsyncClient.
    """
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    return httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        max_redirects=max_redirects,
        # `limits` belongs to the transport, which is supplied below
        transport=_ValidatingAsyncTransport(httpx.AsyncHTTPTransport(limits=limits), allow_localhost),
    )


def validate_authserver_metadata(metadata: t.Dict[str, t.Any], fetch_url: str) -> None:
    """Validate authorization server metadata against ATProto requirements.

    Args:
        metadata: Metadata dictionary from server.
        fetch_url: URL where metadata was fetched from.

    Raises:
        ValueError: If metadata doesn't meet requirements.
    """
    issuer_url = urlparse(metadata['issuer'])
    fetch_parsed = urlparse(fetch_url)

    # Issuer must match fetch URL host
    if issuer_url.hostname != fetch_parsed.hostname:
        raise ValueError(f'Issuer hostname mismatch: {issuer_url.hostname} != {fetch_parsed.hostname}')

    # Issuer must be HTTPS with no path/params/fragment
    if issuer_url.scheme != 'https':
        raise ValueError(f'Issuer must be HTTPS: {issuer_url.scheme}')
    if issuer_url.port is not None:
        raise ValueError(f'Issuer must not have explicit port: {issuer_url.port}')
    if issuer_url.path not in ('', '/'):
        raise ValueError(f'Issuer must not have path: {issuer_url.path}')
    if issuer_url.params or issuer_url.fragment:
        raise ValueError('Issuer must not have params or fragment')

    # Check required grant types and methods
    required_checks = [
        ('code' in metadata.get('response_types_supported', []), 'response_types_supported must include "code"'),
        (
            'authorization_code' in metadata.get('grant_types_supported', []),
            'grant_types_supported must include "authorization_code"',
        ),
        (
            'refresh_token' in metadata.get('grant_types_supported', []),
            'grant_types_supported must include "refresh_token"',
        ),
        (
            'S256' in metadata.get('code_challenge_methods_supported', []),
            'code_challenge_methods_supported must include "S256"',
        ),
        (
            'none' in metadata.get('token_endpoint_auth_methods_supported', []),
            'token_endpoint_auth_methods_supported must include "none"',
        ),
        (
            'private_key_jwt' in metadata.get('token_endpoint_auth_methods_supported', []),
            'token_endpoint_auth_methods_supported must include "private_key_jwt"',
        ),
        (
            'ES256' in metadata.get('token_endpoint_auth_signing_alg_values_supported', []),
            'token_endpoint_auth_signing_alg_values_supported must include "ES256"',
        ),
        ('atproto' in metadata.get('scopes_supported', []), 'scopes_supported must include "atproto"'),
        (
            metadata.get('authorization_response_iss_parameter_supported') is True,
            'authorization_response_iss_parameter_supported must be true',
        ),
        (
            metadata.get('pushed_authorization_request_endpoint') is not None,
            'pushed_authorization_request_endpoint is required',
        ),
        (
            metadata.get('require_pushed_authorization_requests') is True,
            'require_pushed_authorization_requests must be true',
        ),
        (
            'ES256' in metadata.get('dpop_signing_alg_values_supported', []),
            'dpop_signing_alg_values_supported must include "ES256"',
        ),
        (
            metadata.get('client_id_metadata_document_supported') is True,
            'client_id_metadata_document_supported must be true',
        ),
    ]

    for check, error_msg in required_checks:
        if not check:
            raise ValueError(error_msg)
