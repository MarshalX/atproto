import pytest
from atproto_identity.exceptions import DidNotFoundError
from atproto_identity.handle.resolver import HandleResolver

# THESE TESTS ARE NOT MOCKED WITH TEST SERVERS. IT PERFORMS REAL REQUESTS TO THE INTERNET.


def test_handle_resolver() -> None:
    expected_handle = 'test.marshal.dev'
    expected_did_plc = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'

    did_plc = HandleResolver().ensure_resolve(expected_handle)
    assert did_plc == expected_did_plc


def test_handle_resolver_with_invalid_handle_url() -> None:
    expected_handle = 'test123.marshal.dev'

    with pytest.raises(DidNotFoundError):
        HandleResolver().ensure_resolve(expected_handle)


def test_handle_resolver_with_not_existing_well_know() -> None:
    expected_handle = 'feed.atproto.blue'

    with pytest.raises(DidNotFoundError):
        HandleResolver().ensure_resolve(expected_handle)
