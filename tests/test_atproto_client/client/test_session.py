from atproto_client import Session
from atproto_client.client.session import get_session_pds_endpoint


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
