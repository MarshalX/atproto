"""Network mocking for identity resolver tests.

HTTP is intercepted with :class:`httpx.MockTransport`.
DNS is intercepted by monkeypatching.

Any request to an unregistered URL or hostname fails loudly so that a test never silently reaches the real internet.
"""

import typing as t

import dns.asyncresolver
import dns.resolver
import httpx
import pytest

_DID_PLC = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
_DID_PLC_UNKNOWN = 'did:plc:kvwvcn5iqfooopmyzvb41234'
_HANDLE = 'test.marshal.dev'

_DID_WEB_FEED_DOC = (
    '{"@context":["https://www.w3.org/ns/did/v1"],'
    '"id":"did:web:feed.atproto.blue",'
    '"service":[{"id":"#bsky_fg","serviceEndpoint":"https://feed.atproto.blue",'
    '"type":"BskyFeedGenerator"}]}'
)

_DID_PLC_DOC = (
    '{"@context":["https://www.w3.org/ns/did/v1",'
    '"https://w3id.org/security/multikey/v1",'
    '"https://w3id.org/security/suites/secp256k1-2019/v1"],'
    '"id":"did:plc:kvwvcn5iqfooopmyzvb4qzba",'
    '"alsoKnownAs":["at://test.marshal.dev"],'
    '"verificationMethod":[{"id":"did:plc:kvwvcn5iqfooopmyzvb4qzba#atproto",'
    '"type":"Multikey","controller":"did:plc:kvwvcn5iqfooopmyzvb4qzba",'
    '"publicKeyMultibase":"zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j"}],'
    '"service":[{"id":"#atproto_pds","type":"AtprotoPersonalDataServer",'
    '"serviceEndpoint":"https://shimeji.us-east.host.bsky.network"}]}'
)

# Exact URL -> (status_code, body) routes. Everything else raises ConnectError.
_HTTP_ROUTES = {
    'https://feed.atproto.blue/.well-known/did.json': (200, _DID_WEB_FEED_DOC),
    f'https://plc.directory/{_DID_PLC}': (200, _DID_PLC_DOC),
    # Unknown PLC DID: PLC directory replies 404 (resolver maps it to "not found").
    f'https://plc.directory/{_DID_PLC_UNKNOWN}': (404, ''),
}

# DNS qname -> TXT record value. Everything else raises NXDOMAIN.
_DNS_TXT = {
    f'_atproto.{_HANDLE}': 'did=did:plc:kvwvcn5iqfooopmyzvb4qzba',
}


def _http_handler(request: httpx.Request) -> httpx.Response:
    route = _HTTP_ROUTES.get(str(request.url))
    if route is None:
        # accidental real requests fail loudly
        raise httpx.ConnectError(f'No mock for {request.url}', request=request)

    status_code, body = route
    return httpx.Response(status_code, content=body.encode('UTF-8'))


class _FakeRdata:
    def __init__(self, strings: list) -> None:
        self.strings = strings


def _dns_resolve(qname: t.Any, rdtype: t.Any, *args: t.Any, **kwargs: t.Any) -> t.List[_FakeRdata]:
    value = _DNS_TXT.get(str(qname))
    if value is None:
        raise dns.resolver.NXDOMAIN

    return [_FakeRdata([value.encode('UTF-8')])]


async def _dns_resolve_async(qname: t.Any, rdtype: t.Any, *args: t.Any, **kwargs: t.Any) -> t.List[_FakeRdata]:
    return _dns_resolve(qname, rdtype, *args, **kwargs)


@pytest.fixture(autouse=True)
def _mock_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real_client = httpx.Client
    real_async_client = httpx.AsyncClient

    def make_client(*args: t.Any, **kwargs: t.Any) -> httpx.Client:
        kwargs.setdefault('transport', httpx.MockTransport(_http_handler))
        return real_client(*args, **kwargs)

    def make_async_client(*args: t.Any, **kwargs: t.Any) -> httpx.AsyncClient:
        kwargs.setdefault('transport', httpx.MockTransport(_http_handler))
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, 'Client', make_client)
    monkeypatch.setattr(httpx, 'AsyncClient', make_async_client)

    monkeypatch.setattr(dns.resolver, 'resolve', _dns_resolve)
    monkeypatch.setattr(dns.asyncresolver, 'resolve', _dns_resolve_async)
