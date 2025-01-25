import typing as t

from atproto_client.client.client import Client
from atproto_client.client.methods_mixin.headers import _ATPROTO_ACCEPT_LABELERS_HEADER, _ATPROTO_PROXY_HEADER

if t.TYPE_CHECKING:
    from atproto_client import Session, SessionEvent


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


def test_client_clone() -> None:
    client = Client()

    @client.on_session_change
    def session_callback(_: 'SessionEvent', __: 'Session') -> None:
        pass

    cloned_client = client.clone()

    # must be different objects
    assert cloned_client is not client
    assert cloned_client.request is not client.request

    # must be the same shared objects
    assert cloned_client._session is client._session
    assert cloned_client._session_dispatcher is client._session_dispatcher

    # session callbacks must be the same
    assert (
        cloned_client._session_dispatcher._on_session_change_callbacks
        == client._session_dispatcher._on_session_change_callbacks
    )

    # headers must be exact the same
    assert cloned_client.request.get_headers() == client.request.get_headers()
    # header sources must be the same, but different objects
    assert cloned_client.request._additional_header_sources == client.request._additional_header_sources
    assert cloned_client.request._additional_header_sources is not client.request._additional_header_sources
