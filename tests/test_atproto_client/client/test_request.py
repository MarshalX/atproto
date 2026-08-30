import typing as t
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest
from atproto_client import exceptions
from atproto_client.request import AsyncRequest, Request, RequestBase, _handle_response


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
