import ipaddress
import json
import re
import socket
import time
import typing as t
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

from atproto_oauth.exceptions import OAuthRequestError, UnsafeUrlError

DEFAULT_TIMEOUT: t.Final = 10.0
MAX_RESPONSE_SIZE: t.Final = 1024 * 1024

_BLOCKED_HOSTNAMES: t.Final = frozenset({'localhost', 'metadata.google.internal'})
_BLOCKED_SUFFIXES: t.Final = (
    '.localhost',
    '.localdomain',
    '.local',
    '.internal',
    '.intranet',
    '.private',
    '.lan',
    '.home',
    '.corp',
    '.svc',
    '.home.arpa',
)
_DEFAULT_PORTS: t.Final = {'https': 443, 'http': 80}

_HOSTNAME: t.Final = re.compile(r'[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*')
# every label is a number, which the system resolver reads as an IPv4 address in decimal, octal or hexadecimal
_NUMERIC_HOSTNAME: t.Final = re.compile(r'(0x[0-9a-f]*|[0-9]+)(\.(0x[0-9a-f]*|[0-9]+))*')
_NAT64_NETWORK: t.Final = ipaddress.ip_network('64:ff9b::/96')
_IPV4_COMPATIBLE_NETWORK: t.Final = ipaddress.ip_network('::/96')
_IPV4_TRANSLATED_NETWORK: t.Final = ipaddress.ip_network('::ffff:0:0:0/96')
_IPV4_EMBEDDING_NETWORKS: t.Final = (_NAT64_NETWORK, _IPV4_COMPATIBLE_NETWORK, _IPV4_TRANSLATED_NETWORK)

_IpAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


def _parse_ip(hostname: str) -> t.Optional[_IpAddress]:
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        pass

    if not _NUMERIC_HOSTNAME.fullmatch(hostname):
        return None

    try:
        return ipaddress.IPv4Address(socket.inet_aton(hostname))
    except OSError:
        return None


def _unwrap_ipv6(ip: _IpAddress) -> _IpAddress:
    if isinstance(ip, ipaddress.IPv4Address):
        return ip

    if ip.is_loopback or ip.is_unspecified:
        return ip

    if any(ip in network for network in _IPV4_EMBEDDING_NETWORKS):
        return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF)

    return ip.ipv4_mapped or ip.sixtofour or ip


def _is_loopback(hostname: str) -> bool:
    if hostname == 'localhost':
        return True

    ip = _parse_ip(hostname)
    return ip is not None and _unwrap_ipv6(ip).is_loopback


def _is_public(hostname: str, allow_single_label: bool) -> bool:
    if hostname in _BLOCKED_HOSTNAMES or hostname.endswith(_BLOCKED_SUFFIXES):
        return False

    ip = _parse_ip(hostname)
    if ip is None:
        # a numeric last label is an address the resolver understands and this function could not parse
        last_label = hostname.rsplit('.', 1)[-1]
        if last_label.isdigit() or last_label.startswith('0x'):
            return False

        # a name without a dot is resolved through the search domains of the local network
        return (allow_single_label or '.' in hostname) and bool(_HOSTNAME.fullmatch(hostname))

    ip = _unwrap_ipv6(ip)
    # is_global excludes private, loopback, link-local, unique-local and CGNAT ranges; multicast is global
    return ip.is_global and not ip.is_multicast


def is_safe_url(url: str, allow_http: bool = False) -> bool:
    """Tell whether a third-party URL may be requested.

    Only HTTPS URLs of public hosts pass. IP addresses are recognized in the notations
    the system resolver accepts, including hexadecimal, octal and IPv4 embedded in IPv6.

    Warning:
        Only the URL is inspected. A hostname that resolves to a private address passes.

    Args:
        url: URL to check.
        allow_http: Also allow the ``http`` scheme, loopback hosts and names without a dot.
            For development environments.
    """
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
        _ = parts.port
    except ValueError:
        return False

    if not hostname or parts.username is not None or parts.password is not None:
        return False

    if parts.scheme not in {'https', 'http'}:
        return False

    if parts.scheme == 'http' and not allow_http:
        return False

    hostname = hostname.lower().rstrip('.')
    if allow_http and _is_loopback(hostname):
        return True

    return _is_public(hostname, allow_http)


def ensure_safe_url(url: str, allow_http: bool = False) -> None:
    """Raise unless :func:`is_safe_url`.

    Raises:
        :class:`atproto_oauth.exceptions.UnsafeUrlError`: The URL must not be requested.
    """
    if not is_safe_url(url, allow_http):
        raise UnsafeUrlError(f'Refusing to request {url!r}')


def get_origin(url: str) -> str:
    """Return the origin of a URL without the default port.

    Raises:
        :class:`ValueError`: The URL has no scheme or host.
    """
    parts = urlsplit(url)
    if not parts.scheme or not parts.hostname:
        raise ValueError(f'Not an absolute URL: {url!r}')

    hostname = parts.hostname.lower()
    if ':' in hostname:
        hostname = f'[{hostname}]'

    if parts.port is None or parts.port == _DEFAULT_PORTS.get(parts.scheme):
        return f'{parts.scheme}://{hostname}'

    return f'{parts.scheme}://{hostname}:{parts.port}'


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: httpx.Headers
    content: bytes

    def json(self) -> t.Any:
        """Decode the body as JSON, or return :obj:`None` when it is not JSON."""
        try:
            return json.loads(self.content)
        except (ValueError, RecursionError):
            return None

    @property
    def is_json(self) -> bool:
        content_type: str = self.headers.get('content-type', '')
        return content_type.split(';', 1)[0].strip().lower() == 'application/json'


def _client_kwargs(transport: t.Optional[t.Any], timeout: float) -> t.Dict[str, t.Any]:
    kwargs: t.Dict[str, t.Any] = {'timeout': timeout, 'follow_redirects': False}
    if transport is not None:
        kwargs['transport'] = transport

    return kwargs


def _ensure_within_limits(url: str, size: int, deadline: float) -> None:
    if size > MAX_RESPONSE_SIZE:
        raise OAuthRequestError(f'Response of {url!r} is larger than {MAX_RESPONSE_SIZE} bytes')

    # the timeout of httpx restarts with every chunk, which lets a server hold a connection open indefinitely
    if time.monotonic() > deadline:
        raise OAuthRequestError(f'Response of {url!r} took too long')


class HttpClient:
    """HTTP client for requests to third-party URLs. Redirects are not followed.

    Args:
        transport: Transport of the underlying ``httpx.Client``.
        allow_http: See :func:`is_safe_url`.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        transport: t.Optional[httpx.BaseTransport] = None,
        allow_http: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._allow_http = allow_http
        self._timeout = timeout
        self._client = httpx.Client(**_client_kwargs(transport, timeout))

    def request(self, method: str, url: str, **kwargs: t.Any) -> HttpResponse:
        ensure_safe_url(url, self._allow_http)
        deadline = time.monotonic() + self._timeout

        try:
            with self._client.stream(method, url, **kwargs) as response:
                chunks: t.List[bytes] = []
                size = 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    _ensure_within_limits(url, size, deadline)
                    chunks.append(chunk)

                return HttpResponse(response.status_code, response.headers, b''.join(chunks))
        except (httpx.HTTPError, httpx.InvalidURL) as e:
            raise OAuthRequestError(f'Request to {url!r} failed: {e!r}') from e

    def close(self) -> None:
        self._client.close()


class AsyncHttpClient:
    """Asynchronous counterpart of :class:`HttpClient`."""

    def __init__(
        self,
        transport: t.Optional[httpx.AsyncBaseTransport] = None,
        allow_http: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._allow_http = allow_http
        self._timeout = timeout
        self._client = httpx.AsyncClient(**_client_kwargs(transport, timeout))

    async def request(self, method: str, url: str, **kwargs: t.Any) -> HttpResponse:
        ensure_safe_url(url, self._allow_http)
        deadline = time.monotonic() + self._timeout

        try:
            async with self._client.stream(method, url, **kwargs) as response:
                chunks: t.List[bytes] = []
                size = 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    _ensure_within_limits(url, size, deadline)
                    chunks.append(chunk)

                return HttpResponse(response.status_code, response.headers, b''.join(chunks))
        except (httpx.HTTPError, httpx.InvalidURL) as e:
            raise OAuthRequestError(f'Request to {url!r} failed: {e!r}') from e

    async def close(self) -> None:
        await self._client.aclose()
