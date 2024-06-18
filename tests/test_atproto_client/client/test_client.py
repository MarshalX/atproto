from atproto_client.client.client import Client
from atproto_client.client.methods_mixin.headers import _ATPROTO_ACCEPT_LABELERS_HEADER, _ATPROTO_PROXY_HEADER


def test_client_with_bsky_chat_proxy() -> None:
    client = Client()
    dm_client = client.with_bsky_chat_proxy()

    assert _ATPROTO_PROXY_HEADER not in client.request.get_headers()
    assert _ATPROTO_PROXY_HEADER in dm_client.request.get_headers()

    atproto_proxy_header = dm_client.request.get_headers()[_ATPROTO_PROXY_HEADER]
    assert dm_client.AtprotoServiceType.BSKY_CHAT.value in atproto_proxy_header
    assert dm_client.BSKY_CHAT_DID in atproto_proxy_header


def test_client_with_bsky_labeler() -> None:
    client = Client()
    labeled_client = client.with_bsky_labeler()

    assert _ATPROTO_ACCEPT_LABELERS_HEADER not in client.request.get_headers()
    assert _ATPROTO_ACCEPT_LABELERS_HEADER in labeled_client.request.get_headers()

    atproto_accept_labelers_header = labeled_client.request.get_headers()[_ATPROTO_ACCEPT_LABELERS_HEADER]
    assert labeled_client.BSKY_LABELER_DID in atproto_accept_labelers_header


def test_client_with_bsky_chat_and_bsky_labeler() -> None:
    client = Client()
    labeled_client = client.with_bsky_labeler()
    dm_client = labeled_client.with_bsky_chat_proxy()

    assert _ATPROTO_ACCEPT_LABELERS_HEADER not in client.request.get_headers()
    assert _ATPROTO_PROXY_HEADER not in client.request.get_headers()

    assert _ATPROTO_ACCEPT_LABELERS_HEADER in labeled_client.request.get_headers()
    assert _ATPROTO_PROXY_HEADER not in labeled_client.request.get_headers()

    assert _ATPROTO_PROXY_HEADER in dm_client.request.get_headers()
    assert _ATPROTO_ACCEPT_LABELERS_HEADER in dm_client.request.get_headers()
