import pytest
from atproto_identity.did.resolver import AsyncDidResolver

# THESE TESTS ARE NOT MOCKED WITH TEST SERVERS. IT PERFORMS REAL REQUESTS TO THE INTERNET.


@pytest.mark.asyncio
async def test_atproto_data_resolve_atproto_data() -> None:
    expected_did = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    expected_did_key = 'did:key:zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'
    expected_handle = 'test.marshal.dev'

    atproto_data = await AsyncDidResolver().resolve_atproto_data(expected_did)

    assert atproto_data.did == expected_did
    assert atproto_data.signing_key == expected_did_key
    assert atproto_data.handle == expected_handle


@pytest.mark.asyncio
async def test_atproto_data_resolve_atproto_key() -> None:
    did = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'
    expected_did_key = 'did:key:zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'

    did_key = await AsyncDidResolver().resolve_atproto_key(did)
    assert did_key == expected_did_key
