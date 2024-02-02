from atproto_client.client.base import _BASE_API_URL, _handle_base_url


def test_handle_base_url() -> None:
    service_url = 'https://example.com/xrpc'

    assert _handle_base_url() == _BASE_API_URL
    assert _handle_base_url(None) == _BASE_API_URL
    assert _handle_base_url('https://example.com') == service_url
    assert _handle_base_url('https://example.com/') == service_url
    assert _handle_base_url('https://example.com/xrpc') == service_url
