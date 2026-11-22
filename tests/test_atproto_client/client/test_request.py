import typing as t
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest
from atproto_client import exceptions
from atproto_client.request import AsyncRequest, Request, RequestBase, _handle_response, _parse_response


def test_get_headers_case_insensitivity() -> None:
    """Test that get_headers handles case-insensitive header names correctly."""
    req = RequestBase()

    # Add a header with mixed case
    req.add_additional_header('Content-Type', 'application/json')

    # Try to override with a different case
    headers = req.get_headers({'content-type': 'text/plain'})

    # Check that the header was properly overridden
    assert 'content-type' in headers
    assert headers['content-type'] == 'text/plain'
    assert 'Content-Type' not in headers  # No mixed case keys

    # Check that there's only one content-type header (case-insensitive)
    content_type_headers = [k for k in headers if k.lower() == 'content-type']
    assert len(content_type_headers) == 1


def test_add_additional_header_case_insensitivity() -> None:
    """Test that add_additional_header handles case-insensitive header names correctly."""
    req = RequestBase()

    # Add a header with mixed case
    req.add_additional_header('Content-Type', 'application/json')

    # Add the same header with a different case
    req.add_additional_header('content-type', 'text/plain')

    # Get the headers
    headers = req.get_headers()

    # Check that the header was properly overridden
    assert 'content-type' in headers
    assert headers['content-type'] == 'text/plain'
    assert 'Content-Type' not in headers  # No mixed case keys

    # Check that there's only one content-type header (case-insensitive)
    content_type_headers = [k for k in headers if k.lower() == 'content-type']
    assert len(content_type_headers) == 1


def test_set_additional_headers_case_insensitivity() -> None:
    """Test set_additional_headers."""
    req = RequestBase()

    # Set headers with a mixed case
    req.set_additional_headers(
        {'Content-Type': 'application/json', 'AUTHORIZATION': 'Bearer token', 'accept': 'application/json'}
    )

    # Get the headers
    headers = req.get_headers()

    # Check that all headers are present
    assert 'Content-Type' in headers
    assert 'AUTHORIZATION' in headers
    assert 'accept' in headers

    # Check values
    assert headers['Content-Type'] == 'application/json'
    assert headers['AUTHORIZATION'] == 'Bearer token'
    assert headers['accept'] == 'application/json'


def test_headers_override_with_additional_headers() -> None:
    """Test that additional headers properly override existing headers."""
    req = RequestBase()

    # Add some headers
    req.add_additional_header('content-type', 'application/json')
    req.add_additional_header('authorization', 'Bearer token1')

    # Override with additional headers
    headers = req.get_headers({'Content-Type': 'text/plain', 'AUTHORIZATION': 'Bearer token2'})

    # Check that headers were properly overridden
    assert headers['Content-Type'] == 'text/plain'
    assert headers['AUTHORIZATION'] == 'Bearer token2'

    # Check that there are no duplicate headers with different cases
    assert len([k for k in headers if k.lower() == 'content-type']) == 1
    assert len([k for k in headers if k.lower() == 'authorization']) == 1


def test_headers_from_sources() -> None:
    """Test that headers from sources are properly handled."""
    req = RequestBase()

    # Add a header source
    req.add_additional_headers_source(lambda: {'Content-Type': 'application/json'})

    # Add another header source with a different case
    req.add_additional_headers_source(lambda: {'content-type': 'text/plain'})

    # Get the headers
    headers = req.get_headers()

    # Check that the last source's value is used
    assert headers['content-type'] == 'text/plain'

    # Check that the first source's value is not used
    assert 'Content-Type' not in headers

    # Check that there are no duplicate headers with different cases
    assert len([k for k in headers if k.lower() == 'content-type']) == 1


def test_clone_keeps_httpx_client_config() -> None:
    timeout = httpx.Timeout(30.0)

    request = Request(timeout=timeout)
    cloned_request = request.clone()

    assert cloned_request is not request
    assert cloned_request._client is not request._client
    assert cloned_request._client.timeout == timeout


def test_async_clone_keeps_httpx_client_config() -> None:
    timeout = httpx.Timeout(30.0)

    request = AsyncRequest(timeout=timeout)
    cloned_request = request.clone()

    assert cloned_request is not request
    assert cloned_request._client is not request._client
    assert cloned_request._client.timeout == timeout


def test_clone_of_clone_keeps_httpx_client_config() -> None:
    timeout = httpx.Timeout(30.0)

    request = Request(timeout=timeout).clone().clone()

    assert request._client.timeout == timeout


@pytest.mark.parametrize('body', [b'{', b'', b'[' * 250 + b']' * 250], ids=['cut short', 'empty', 'nested too deep'])
def test_response_with_malformed_json_is_a_request_exception(body: bytes) -> None:
    response = httpx.Response(200, content=body, headers={'content-type': 'application/json'})

    with pytest.raises(exceptions.RequestException) as exc_info:
        _parse_response(response)

    error = exc_info.value
    assert error.response is not None
    assert not error.response.success
    assert error.response.status_code == 200
    assert error.response.content == body
    assert error.response.headers['content-type'] == 'application/json'


_URL = 'https://bsky.social/xrpc/com.atproto.server.describeServer'

_TRANSPORT_FAILURES = [
    pytest.param(httpx.ReadTimeout('boom'), exceptions.InvokeTimeoutError, id='timeout'),
    pytest.param(httpx.ConnectError('boom'), exceptions.NetworkError, id='refused connection'),
    pytest.param(httpx.RemoteProtocolError('boom'), exceptions.NetworkError, id='protocol violation'),
    pytest.param(httpx.UnsupportedProtocol('boom'), exceptions.NetworkError, id='unsupported protocol'),
    pytest.param(httpx.ProxyError('boom'), exceptions.NetworkError, id='proxy failure'),
    pytest.param(httpx.TooManyRedirects('boom'), exceptions.NetworkError, id='too many redirects'),
    pytest.param(httpx.DecodingError('boom'), exceptions.NetworkError, id='malformed encoding'),
]


def _redirect_to_itself(request: httpx.Request) -> httpx.Response:
    return httpx.Response(302, headers={'location': str(request.url)})


def _redirect_to_a_malformed_url(_: httpx.Request) -> httpx.Response:
    return httpx.Response(302, headers={'location': 'https://[::1'})


def _respond_with_a_malformed_encoding(_: httpx.Request) -> httpx.Response:
    return httpx.Response(200, headers={'content-encoding': 'gzip'}, content=b'not gzip')


_MISBEHAVING_HOSTS = [
    pytest.param(_redirect_to_itself, id='redirect loop'),
    pytest.param(_redirect_to_a_malformed_url, id='malformed redirect'),
    pytest.param(_respond_with_a_malformed_encoding, id='malformed encoding'),
]


def _check_transport_failure(error: exceptions.NetworkError, expected: t.Type[exceptions.NetworkError]) -> None:
    assert type(error) is expected
    assert error.response is None
    assert isinstance(error.__cause__, httpx.HTTPError)


@pytest.mark.parametrize(('failure', 'expected'), _TRANSPORT_FAILURES)
def test_transport_failure_is_a_network_error(
    failure: httpx.HTTPError, expected: t.Type[exceptions.NetworkError]
) -> None:
    def handle(_: httpx.Request) -> httpx.Response:
        raise failure

    request = Request(transport=httpx.MockTransport(handle))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        request.get(_URL)

    _check_transport_failure(exc_info.value, expected)


@pytest.mark.asyncio
@pytest.mark.parametrize(('failure', 'expected'), _TRANSPORT_FAILURES)
async def test_async_transport_failure_is_a_network_error(
    failure: httpx.HTTPError, expected: t.Type[exceptions.NetworkError]
) -> None:
    def handle(_: httpx.Request) -> httpx.Response:
        raise failure

    request = AsyncRequest(transport=httpx.MockTransport(handle))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        await request.get(_URL)

    _check_transport_failure(exc_info.value, expected)


@pytest.mark.parametrize('handle', _MISBEHAVING_HOSTS)
def test_misbehaving_host_is_a_network_error(handle: t.Callable[[httpx.Request], httpx.Response]) -> None:
    request = Request(transport=httpx.MockTransport(handle))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        request.get(_URL)

    _check_transport_failure(exc_info.value, exceptions.NetworkError)


@pytest.mark.asyncio
@pytest.mark.parametrize('handle', _MISBEHAVING_HOSTS)
async def test_async_misbehaving_host_is_a_network_error(handle: t.Callable[[httpx.Request], httpx.Response]) -> None:
    request = AsyncRequest(transport=httpx.MockTransport(handle))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        await request.get(_URL)

    _check_transport_failure(exc_info.value, exceptions.NetworkError)


_MALFORMED_URLS = [
    pytest.param('https://bsky.social:8a/xrpc', id='port'),
    pytest.param('https://bsky.social\x00/xrpc', id='control character'),
    pytest.param(f'https://bsky.social/{"a" * 70000}', id='too long'),
]


@pytest.mark.parametrize('url', _MALFORMED_URLS)
def test_malformed_url_is_a_network_error(url: str) -> None:
    request = Request(transport=httpx.MockTransport(_redirect_to_itself))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        request.get(url)

    assert exc_info.value.response is None
    assert isinstance(exc_info.value.__cause__, httpx.InvalidURL)


@pytest.mark.asyncio
@pytest.mark.parametrize('url', _MALFORMED_URLS)
async def test_async_malformed_url_is_a_network_error(url: str) -> None:
    request = AsyncRequest(transport=httpx.MockTransport(_redirect_to_itself))

    with pytest.raises(exceptions.NetworkError) as exc_info:
        await request.get(url)

    assert exc_info.value.response is None
    assert isinstance(exc_info.value.__cause__, httpx.InvalidURL)


def test_error_that_is_not_of_the_transport_is_raised_as_is() -> None:
    def handle(_: httpx.Request) -> httpx.Response:
        raise RuntimeError('boom')

    request = Request(transport=httpx.MockTransport(handle))

    with pytest.raises(RuntimeError, match='boom'):
        request.get(_URL)


def _raise_for_status(status_code: int, headers: t.Optional[t.Dict[str, str]] = None) -> None:
    _handle_response(httpx.Response(status_code, headers=headers, request=httpx.Request('GET', 'https://bsky.social')))


def test_rate_limit_exceeded_error() -> None:
    with pytest.raises(exceptions.RateLimitExceededError):
        _raise_for_status(429)


def test_rate_limit_exceeded_error_is_a_request_exception() -> None:
    with pytest.raises(exceptions.RequestException):
        _raise_for_status(429)


def test_rate_limit_exceeded_error_budget() -> None:
    headers = {
        'ratelimit-limit': '3000',
        'ratelimit-remaining': '0',
        'ratelimit-reset': '1735689600',
        'ratelimit-policy': '3000;w=300',
    }

    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, headers)

    error = exc_info.value
    assert error.limit == 3000
    assert error.remaining == 0
    assert error.reset_at == datetime(2025, 1, 1, tzinfo=timezone.utc)
    assert error.policy == '3000;w=300'


def test_rate_limit_exceeded_error_without_budget_headers() -> None:
    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429)

    error = exc_info.value
    assert error.limit is None
    assert error.remaining is None
    assert error.reset_at is None
    assert error.policy is None


def test_rate_limit_exceeded_error_with_malformed_budget_headers() -> None:
    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, {'ratelimit-limit': 'nope', 'ratelimit-reset': 'nope'})

    assert exc_info.value.limit is None
    assert exc_info.value.reset_at is None


def test_rate_limit_exceeded_error_retry_after_seconds() -> None:
    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, {'retry-after': '12'})

    assert exc_info.value.retry_after == 12.0


def test_rate_limit_exceeded_error_retry_after_http_date() -> None:
    retry_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, {'retry-after': format_datetime(retry_at, usegmt=True)})

    retry_after = exc_info.value.retry_after
    assert retry_after is not None
    assert 55 <= retry_after <= 60


def test_rate_limit_exceeded_error_retry_after_in_the_past_is_not_negative() -> None:
    retry_at = datetime.now(timezone.utc) - timedelta(seconds=60)

    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, {'retry-after': format_datetime(retry_at, usegmt=True)})

    assert exc_info.value.retry_after == 0.0


@pytest.mark.parametrize('value', ['soon', '', 'nan', 'inf'])
def test_rate_limit_exceeded_error_retry_after_is_none_when_unusable(value: str) -> None:
    with pytest.raises(exceptions.RateLimitExceededError) as exc_info:
        _raise_for_status(429, {'retry-after': value})

    assert exc_info.value.retry_after is None


def test_rate_limit_exceeded_error_without_response() -> None:
    error = exceptions.RateLimitExceededError()

    assert error.limit is None
    assert error.reset_at is None
    assert error.policy is None
    assert error.retry_after is None
