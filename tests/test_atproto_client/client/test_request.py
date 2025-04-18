from atproto_client.request import RequestBase


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
