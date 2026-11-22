import typing as t

import httpx
import pytest
from atproto_client import models
from atproto_client.exceptions import BadRequestError, RequestException
from atproto_client.models.dot_dict import DotDict
from atproto_client.request import AsyncRequest
from atproto_crypto.multibase import bytes_to_multibase
from atproto_space import AsyncSpaceReader
from atproto_space.exceptions import SpaceIdentityError, SpaceMacError, SpaceRepoVerificationError
from atproto_space.mac import COMMIT_MAC_PROFILE, RECORD_MAC_PROFILE
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    AsyncFakeIdResolver,
    FakeSpaceNetwork,
    build_network,
    delegation_token_provider,
    parse_mac_request,
)

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_GET_RECORD = 'com.atproto.space.getRecord'
_GET_LATEST_COMMIT = 'com.atproto.space.getLatestCommit'
_GET_BLOB = 'com.atproto.space.getBlob'

_NOTE = 'com.example.note'
_NOTE_VALUE = {'$type': _NOTE, 'text': 'hello'}
_URI = f'{SPACE}/{BOB_DID}/{_NOTE}/b'

_OTHER_REV = '3jzfcijpj2z2a'
# CID of the record {'text': 'hello'}
_OTHER_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
# CID of the raw bytes b'hello'
_OTHER_BLOB_CID = 'bafkreibm6jg3ux5qumhcn2b3flc3tyu6dmlb4xa7u5bf44yegnrjhc4yeq'

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L593-L635
_BLOB = bytes([1, 2, 3, 4, 5])
_BLOB_TYPE = 'image/png'
_WRONG_BLOB = bytes([6, 6, 6])

_P256_PREFIX = b'\x80\x24'
_UNCOMPRESSED_POINT = b'\x04' + b'\xff' * 64
# KEM methods of a DID document that hold no P-256 key
_MALFORMED_KEM_METHODS = [
    pytest.param(('Multikey', '!!!'), id='not multibase'),
    pytest.param(
        ('Multikey', bytes_to_multibase('z', _P256_PREFIX + _UNCOMPRESSED_POINT)), id='point that is not compressed'
    ),
]

_Read = t.Callable[[AsyncSpaceReader], t.Awaitable[object]]
_Edit = t.Callable[[t.Dict[str, t.Any]], None]


def make_reader(network: FakeSpaceNetwork, **kwargs: t.Any) -> AsyncSpaceReader:
    kwargs.setdefault('delegation_token_provider', delegation_token_provider(network, ALICE_DID))
    kwargs.setdefault('id_resolver', AsyncFakeIdResolver(network))
    kwargs.setdefault('request', AsyncRequest(transport=network.async_transport))

    return AsyncSpaceReader(SPACE, **kwargs)


@pytest.fixture
def network() -> FakeSpaceNetwork:
    network = build_network()
    network.put_record(SPACE, BOB_DID, _NOTE, 'b', _NOTE_VALUE)

    return network


async def _get_record(reader: AsyncSpaceReader) -> object:
    return await reader.get_record(_NOTE, 'b', BOB_DID)


async def _get_latest_commit(reader: AsyncSpaceReader) -> object:
    return await reader.get_latest_commit(BOB_DID)


# the reads that are verified against a MAC
_MAC_READS = [
    pytest.param(_GET_RECORD, _get_record, id='record'),
    pytest.param(_GET_LATEST_COMMIT, _get_latest_commit, id='commit'),
]
_MAC_PROFILES = {_GET_RECORD: RECORD_MAC_PROFILE, _GET_LATEST_COMMIT: COMMIT_MAC_PROFILE}


def _key_shares(network: FakeSpaceNetwork, nsid: str) -> t.List[str]:
    key_shares: t.List[str] = []
    for request in network.requests_to(nsid):
        mac_request = parse_mac_request(request.headers['accept-signature'], _MAC_PROFILES[nsid])
        assert mac_request is not None
        key_shares.append(mac_request.key_share)

    return key_shares


def _tamper(network: FakeSpaceNetwork, nsid: str, edit: _Edit) -> AsyncRequest:
    """Build the HTTP client of a reader that gets the responses to a method with a changed body and the same MAC."""

    async def handle(request: httpx.Request) -> httpx.Response:
        response = await network.handle_async(request)
        if not request.url.path.endswith(nsid):
            return response

        body = response.json()
        edit(body)
        headers = {name: value for name, value in response.headers.items() if name != 'content-length'}

        return httpx.Response(response.status_code, json=body, headers=headers)

    return AsyncRequest(transport=httpx.MockTransport(handle))


@pytest.mark.asyncio
async def test_get_record_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    record = await reader.get_record(_NOTE, 'b', BOB_DID)

    request = network.requests_to(_GET_RECORD)[0]
    key_share = _key_shares(network, _GET_RECORD)[0]
    assert isinstance(record, models.ComAtprotoSpaceGetRecord.Response)
    assert (record.uri, record.cid) == (_URI, network.repos[(SPACE, BOB_DID)].records[f'{_NOTE}/b'].cid)
    assert record.value == DotDict(_NOTE_VALUE)
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200), (BOB_PDS, _GET_RECORD, 200)]
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID, 'collection': _NOTE, 'rkey': 'b'}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert request.headers['accept-signature'] == (
        f'mac=("atproto-space-record";sf);keyid="{key_share}";tag="atproto-space-record"'
    )
    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, False), (AUTHORITY_DID, False)]


@pytest.mark.asyncio
async def test_get_latest_commit_asks_the_pds_of_the_repo_for_a_mac(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    commit = await reader.get_latest_commit(BOB_DID)

    request = network.requests_to(_GET_LATEST_COMMIT)[0]
    key_share = _key_shares(network, _GET_LATEST_COMMIT)[0]
    assert commit == models.ComAtprotoSpaceDefs.Commit(**network.get_commit(SPACE, BOB_DID))
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200), (BOB_PDS, _GET_LATEST_COMMIT, 200)]
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert request.headers['accept-signature'] == (
        f'mac=("atproto-space-commit";sf);keyid="{key_share}";tag="atproto-space-commit"'
    )


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L609-L617
@pytest.mark.asyncio
async def test_get_blob_asks_the_pds_of_the_repo(network: FakeSpaceNetwork) -> None:
    cid = network.add_blob(SPACE, BOB_DID, _BLOB, _BLOB_TYPE)
    reader = make_reader(network)

    blob = await reader.get_blob(cid, BOB_DID)

    request = network.requests_to(_GET_BLOB)[0]
    assert blob == _BLOB
    assert network.log == [(AUTHORITY_PDS, _AUTHORIZE, 200), (BOB_PDS, _GET_BLOB, 200)]
    assert dict(request.url.params) == {'space': SPACE, 'repo': BOB_DID, 'cid': cid}
    assert request.headers['atproto-space-audience'] == BOB_DID
    assert 'accept-signature' not in request.headers


@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read'), _MAC_READS)
async def test_rejected_credential_is_renewed_and_the_read_retried_with_another_key_share(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    reader = make_reader(network)
    await reader.authorize()
    network.revoke_credentials()

    await read(reader)

    rejected, retried = _key_shares(network, nsid)
    assert network.count(_AUTHORIZE) == 2
    assert network.statuses(nsid) == [401, 200]
    assert rejected != retried


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L384-L425
@pytest.mark.asyncio
@pytest.mark.parametrize('knob', ['drop_mac', 'corrupt_mac'])
@pytest.mark.parametrize(('nsid', 'read'), _MAC_READS)
async def test_response_without_a_valid_mac_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, nsid: str, read: _Read, knob: str
) -> None:
    setattr(network, knob, True)
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(SpaceRepoVerificationError, match='failed verification') as error:
        await read(reader)

    first, second = _key_shares(network, nsid)
    assert isinstance(error.value.__cause__, SpaceMacError)
    assert network.statuses(nsid) == [200, 200]
    assert network.count(_AUTHORIZE) == 1
    assert first != second
    assert resolver.did.calls == [
        (BOB_DID, False),
        (BOB_DID, False),
        (AUTHORITY_DID, False),
        (BOB_DID, True),
        (BOB_DID, False),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read'), _MAC_READS)
async def test_rotated_kem_key_is_resolved_again(network: FakeSpaceNetwork, nsid: str, read: _Read) -> None:
    resolver = AsyncFakeIdResolver(network, cache=True)
    reader = make_reader(network, id_resolver=resolver)
    await read(reader)
    network.accounts[BOB_DID].kem_key = ec.generate_private_key(ec.SECP256R1())
    resolver.did.calls.clear()

    await read(reader)

    assert network.statuses(nsid) == [200, 200, 200]
    assert network.count(_AUTHORIZE) == 1
    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, False), (BOB_DID, True), (BOB_DID, False)]


@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read'), _MAC_READS)
async def test_account_without_a_kem_key_is_resolved_again_and_costs_no_request(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    network.accounts[BOB_DID].kem_key = None
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(SpaceIdentityError, match=f'DID document of {BOB_DID} has no usable #atproto_kem key'):
        await read(reader)

    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, True)]
    assert network.count(nsid) == 0
    assert network.count(_AUTHORIZE) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('kem_method', _MALFORMED_KEM_METHODS)
async def test_account_with_a_malformed_kem_key_is_resolved_again_and_costs_no_request(
    network: FakeSpaceNetwork, kem_method: t.Tuple[str, str]
) -> None:
    network.accounts[BOB_DID].kem_method = kem_method
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(SpaceIdentityError, match=f'DID document of {BOB_DID} has no usable #atproto_kem key'):
        await reader.get_latest_commit(BOB_DID)

    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, True)]
    assert network.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(('nsid', 'read'), _MAC_READS)
async def test_kem_key_added_after_the_did_document_was_cached_is_found(
    network: FakeSpaceNetwork, nsid: str, read: _Read
) -> None:
    bob = network.accounts[BOB_DID]
    kem_key, bob.kem_key = bob.kem_key, None
    resolver = AsyncFakeIdResolver(network, cache=True)
    await resolver.did.ensure_resolve(BOB_DID)
    bob.kem_key = kem_key
    resolver.did.calls.clear()
    reader = make_reader(network, id_resolver=resolver)

    await read(reader)

    assert network.statuses(nsid) == [200]
    assert resolver.did.calls == [(BOB_DID, False), (BOB_DID, True), (BOB_DID, False), (AUTHORITY_DID, False)]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('changes', 'reason'),
    [
        pytest.param(
            {'uri': f'{SPACE}/{BOB_DID}/{_NOTE}/c'},
            f'Record is not the one requested: {SPACE}/{BOB_DID}/{_NOTE}/c',
            id='uri',
        ),
        pytest.param({'cid': _OTHER_CID}, 'Record does not match its MAC', id='cid'),
        pytest.param({'value': {'$type': _NOTE, 'text': 'bye'}}, 'Record value does not match its CID', id='value'),
    ],
)
async def test_record_changed_by_the_host_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, changes: t.Dict[str, t.Any], reason: str
) -> None:
    reader = make_reader(network, request=_tamper(network, _GET_RECORD, lambda body: body.update(changes)))

    with pytest.raises(SpaceRepoVerificationError, match=f'Record {_URI} failed verification') as error:
        await reader.get_record(_NOTE, 'b', BOB_DID)

    assert str(error.value.__cause__) == reason
    assert network.statuses(_GET_RECORD) == [200, 200]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('changes', 'reason'),
    [
        pytest.param({'repo': ALICE_DID}, f'Commit is for another repo: {ALICE_DID}', id='repo'),
        pytest.param({'rev': _OTHER_REV}, 'Commit does not match its MAC', id='rev'),
    ],
)
async def test_commit_changed_by_the_host_is_rejected_after_one_retry(
    network: FakeSpaceNetwork, changes: t.Dict[str, t.Any], reason: str
) -> None:
    reader = make_reader(
        network, request=_tamper(network, _GET_LATEST_COMMIT, lambda body: body['commit'].update(changes))
    )

    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification') as error:
        await reader.get_latest_commit(BOB_DID)

    assert str(error.value.__cause__) == reason
    assert network.statuses(_GET_LATEST_COMMIT) == [200, 200]


@pytest.mark.asyncio
async def test_error_of_the_host_is_not_retried(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(BadRequestError, match='RecordNotFound'):
        await reader.get_record(_NOTE, 'missing', BOB_DID)

    assert network.statuses(_GET_RECORD) == [400]


@pytest.mark.asyncio
async def test_response_that_is_not_json_fails_verification_without_a_retry(network: FakeSpaceNetwork) -> None:
    headers = {'content-type': 'application/json'}
    network.forced_responses[_GET_RECORD] = [httpx.Response(200, content=b'{', headers=headers)]
    network.forced_responses[_GET_LATEST_COMMIT] = [httpx.Response(200, content=b'[' * 250, headers=headers)]
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Record {_URI} failed verification') as error:
        await reader.get_record(_NOTE, 'b', BOB_DID)
    with pytest.raises(SpaceRepoVerificationError, match=f'Repo {BOB_DID} commit failed verification'):
        await reader.get_latest_commit(BOB_DID)

    assert isinstance(error.value.__cause__, RequestException)
    assert network.count(_GET_RECORD) == 1
    assert network.count(_GET_LATEST_COMMIT) == 1


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/tests/space-client.test.ts#L619-L635
@pytest.mark.asyncio
async def test_blob_that_does_not_match_its_cid_is_rejected(network: FakeSpaceNetwork) -> None:
    cid = network.add_blob(SPACE, BOB_DID, _BLOB, _BLOB_TYPE)
    network.repos[(SPACE, BOB_DID)].blobs[cid] = (_WRONG_BLOB, _BLOB_TYPE)
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Blob {cid} failed verification'):
        await reader.get_blob(cid, BOB_DID)

    assert network.statuses(_GET_BLOB) == [200]


@pytest.mark.asyncio
@pytest.mark.parametrize('blob', [b'{"text": "hello"}', b'{'], ids=['json', 'malformed-json'])
async def test_blob_served_as_json_is_rejected(network: FakeSpaceNetwork, blob: bytes) -> None:
    cid = network.add_blob(SPACE, BOB_DID, blob, 'application/json')
    reader = make_reader(network)

    with pytest.raises(SpaceRepoVerificationError, match=f'Blob {cid} failed verification'):
        await reader.get_blob(cid, BOB_DID)

    assert network.statuses(_GET_BLOB) == [200]


@pytest.mark.asyncio
async def test_blob_that_the_host_does_not_have_is_not_a_verification_failure(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(BadRequestError, match='BlobNotFound'):
        await reader.get_blob(_OTHER_BLOB_CID, BOB_DID)

    assert network.statuses(_GET_BLOB) == [400]


@pytest.mark.asyncio
@pytest.mark.parametrize('cid', [pytest.param(_OTHER_CID, id='dag-cbor'), pytest.param('blob', id='malformed')])
async def test_get_blob_refuses_a_cid_that_is_not_a_cid_of_a_blob(network: FakeSpaceNetwork, cid: str) -> None:
    resolver = AsyncFakeIdResolver(network)
    reader = make_reader(network, id_resolver=resolver)

    with pytest.raises(ValueError, match='is not a CID of a blob'):
        await reader.get_blob(cid, BOB_DID)

    assert network.requests == []
    assert resolver.did.calls == []


@pytest.mark.asyncio
async def test_verified_reads_require_the_repo(network: FakeSpaceNetwork) -> None:
    reader = make_reader(network)

    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.get_record(_NOTE, 'b')
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.get_latest_commit()
    with pytest.raises(ValueError, match='repo to read is required'):
        await reader.get_blob(_OTHER_BLOB_CID)

    assert network.requests == []
