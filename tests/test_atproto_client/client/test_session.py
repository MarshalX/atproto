import pytest
from atproto_client import Session
from atproto_client.client.session import SessionDispatcher, SessionEvent, get_session_pds_endpoint


def test_session_old_format_migration() -> None:
    expected_pds = 'https://bsky.social'
    session_string_old = 'handle:::did:::access_jwt:::refresh_jwt'
    session_string_new = f'handle:::did:::access_jwt:::refresh_jwt:::{expected_pds}'

    session = Session.decode(session_string_old)

    assert session.handle == 'handle'
    assert session.did == 'did'
    assert session.access_jwt == 'access_jwt'
    assert session.refresh_jwt == 'refresh_jwt'
    assert session.pds_endpoint == expected_pds

    assert session.encode() == session_string_new


def test_session_roundtrip() -> None:
    session_string = 'handle:::did:::access_jwt:::refresh_jwt:::https://blabla.bla'
    session = Session.decode(session_string)
    assert session.encode() == session_string


def test_session_copy() -> None:
    session_string = 'handle:::did:::access_jwt:::refresh_jwt:::https://blabla.bla'
    session = Session.decode(session_string)
    session_copy = session.copy()

    assert session_copy.handle == session.handle
    assert session_copy.did == session.did
    assert session_copy.access_jwt == session.access_jwt
    assert session_copy.refresh_jwt == session.refresh_jwt
    assert session_copy.pds_endpoint == session.pds_endpoint

    assert session_copy.encode() == session.encode()


def test_get_session_pds_endpoint() -> None:
    expected_pds = 'https://blabla.bla'
    session = Session('handle', 'did', 'access_jwt', 'refresh_jwt', expected_pds)
    assert get_session_pds_endpoint(session) == expected_pds

    session = Session('handle', 'did', 'access_jwt', 'refresh_jwt')
    assert get_session_pds_endpoint(session) == 'https://bsky.social'


_TEST_HANDLE = 'test_handle'


@pytest.fixture
def session() -> Session:
    return Session(handle=_TEST_HANDLE, did='test_did', access_jwt='access_token', refresh_jwt='refresh_token')


@pytest.fixture
def dispatcher(session: Session) -> SessionDispatcher:
    return SessionDispatcher(session)


def test_register_sync_callback(dispatcher: SessionDispatcher) -> None:
    callback_called = False

    def sync_callback(event: SessionEvent, session: Session) -> None:
        nonlocal callback_called
        callback_called = True

        assert session.handle == _TEST_HANDLE
        assert event == SessionEvent.CREATE

    dispatcher.on_session_change(sync_callback)
    dispatcher.dispatch_session_change(SessionEvent.CREATE)

    assert callback_called


@pytest.mark.asyncio
async def test_register_async_callback(dispatcher: SessionDispatcher) -> None:
    callback_called = False

    async def async_callback(event: SessionEvent, session: Session) -> None:
        nonlocal callback_called
        callback_called = True

        assert session.handle == _TEST_HANDLE
        assert event == SessionEvent.REFRESH

    dispatcher.on_session_change(async_callback)
    await dispatcher.dispatch_session_change_async(SessionEvent.REFRESH)

    assert callback_called


def test_session_not_modified(dispatcher: SessionDispatcher) -> None:
    initial_handle = dispatcher._session.handle

    @dispatcher.on_session_change
    def sync_callback(_: SessionEvent, session: Session) -> None:
        session.handle = 'modified_handle'  # This should not affect the original session

    dispatcher.dispatch_session_change(SessionEvent.IMPORT)

    assert dispatcher._session.handle == initial_handle  # The original session remains unchanged


@pytest.mark.asyncio
async def test_async_session_not_modified(dispatcher: SessionDispatcher) -> None:
    initial_handle = dispatcher._session.handle

    @dispatcher.on_session_change
    async def async_callback(_: SessionEvent, session: Session) -> None:
        session.handle = 'modified_handle'  # This should not affect the original session

    await dispatcher.dispatch_session_change_async(SessionEvent.CREATE)

    assert dispatcher._session.handle == initial_handle  # The original session remains unchanged
