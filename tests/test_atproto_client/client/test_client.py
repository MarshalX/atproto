import httpx
import pytest
from atproto_client import Session, SessionEvent
from atproto_client.client.async_client import AsyncClient
from atproto_client.client.client import Client
from atproto_client.client.methods_mixin.headers import _ATPROTO_ACCEPT_LABELERS_HEADER, _ATPROTO_PROXY_HEADER
from atproto_client.request import Request


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


def _log_in(client: Client) -> 'Session':
    session = Session(handle='test.bsky.social', did='did:plc:test', access_jwt='access', refresh_jwt='refresh')
    client._session_dispatcher.set_session(session)

    return session


def test_client_clone_before_login_is_authenticated() -> None:
    client = Client()
    cloned_client = client.clone()

    assert 'Authorization' not in cloned_client.request.get_headers()

    session = _log_in(client)

    assert cloned_client.request.get_headers()['Authorization'] == 'Bearer access'
    assert cloned_client._session is session
    assert cloned_client.export_session_string() == client.export_session_string()


def test_client_clone_before_login_shares_session_callbacks() -> None:
    client = Client()
    cloned_client = client.clone()

    events = []

    @cloned_client.on_session_change
    def session_callback(event: 'SessionEvent', _: 'Session') -> None:
        events.append(event)

    _log_in(client)
    client._call_on_session_change_callbacks(SessionEvent.CREATE)

    assert events == [SessionEvent.CREATE]


def test_client_clone_registers_the_auth_headers_source_once() -> None:
    client = Client()
    cloned_client = client.with_bsky_labeler().with_bsky_chat_proxy()

    assert len(cloned_client.request._additional_header_sources) == 1
    assert cloned_client.request._additional_header_sources == client.request._additional_header_sources


def test_client_clone_keeps_request_config() -> None:
    timeout = httpx.Timeout(30.0)

    client = Client(request=Request(timeout=timeout))
    cloned_client = client.with_bsky_chat_proxy()

    assert cloned_client.request._client.timeout == timeout


@pytest.mark.asyncio
async def test_async_client_clone_before_login_is_authenticated() -> None:
    client = AsyncClient()
    cloned_client = client.clone()

    session = Session(handle='test.bsky.social', did='did:plc:test', access_jwt='access', refresh_jwt='refresh')
    client._session_dispatcher.set_session(session)

    assert cloned_client.request.get_headers()['Authorization'] == 'Bearer access'
    assert cloned_client._session is session
