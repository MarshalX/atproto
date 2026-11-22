import asyncio
import base64
import hashlib
import hmac
import threading
import time
import typing as t

import httpx
import pytest
from atproto_client import models
from atproto_client.models.utils import get_or_create
from atproto_core.star import STAR
from atproto_crypto.algs import P256
from atproto_crypto.did import private_key_to_did_key
from atproto_crypto.kem import Encapsulation, encapsulate
from atproto_identity.exceptions import DidNotFoundError
from atproto_space import SpaceCredential
from atproto_space.commit import RepoCommit, verify_commit
from atproto_space.exceptions import SpaceMacError, SpaceRepoVerificationError
from atproto_space.mac import verify_commit_mac, verify_record_mac
from atproto_space.models import RepoRecord
from atproto_space.repo_archive import read_repo_archive, verify_repo_archive_records
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.fake_space import (
    ALICE_DID,
    ALICE_PDS,
    AUTHORITY_DID,
    AUTHORITY_PDS,
    BOB_DID,
    BOB_PDS,
    SPACE,
    Account,
    AsyncFakeIdResolver,
    FakeIdResolver,
    FakeSpaceNetwork,
    MacRequest,
    Repo,
    async_fake_client,
    async_fake_password_client,
    build_network,
    create_commit_mac_headers,
    create_record_mac_headers,
    fake_client,
    fake_password_client,
    parse_mac_request,
)
from tests.test_atproto_space.token_builder import build_delegation_token, build_space_credential

_AUTHORIZE = 'com.atproto.space.authorizeSpaceSync'
_LIST_WRITERS = 'com.atproto.space.listWriters'
_LIST_RECORDS = 'com.atproto.space.listRecords'
_LIST_BLOBS = 'com.atproto.space.listBlobs'
_GET_RECORD = 'com.atproto.space.getRecord'
_GET_LATEST_COMMIT = 'com.atproto.space.getLatestCommit'
_GET_BLOB = 'com.atproto.space.getBlob'
_GET_REPO = 'com.atproto.space.getRepo'
_LIST_REPO_OPS = 'com.atproto.space.listRepoOps'
_GET_DELEGATION_TOKEN = 'com.atproto.space.getDelegationToken'
_CREATE_RECORD = 'com.atproto.space.createRecord'
_APPLY_WRITES = 'com.atproto.space.applyWrites'
_CREATE_SPACE = 'com.atproto.space.createSpace'
_GET_SPACE = 'com.atproto.space.getSpace'
_UPDATE_SPACE = 'com.atproto.space.updateSpace'
_DELETE_SPACE = 'com.atproto.space.deleteSpace'
_REMOVE_WRITER = 'com.atproto.space.removeWriter'
_LIST_MEMBERS = 'com.atproto.memberspace.listMembers'
_PUT_MEMBERS = 'com.atproto.memberspace.putMembers'
_REMOVE_MEMBERS = 'com.atproto.memberspace.removeMembers'
_CREATE_SESSION = 'com.atproto.server.createSession'

_MEMBERSPACE_POLICY = {'$type': 'com.atproto.memberspace.policy'}
_PERSONALSPACE_POLICY = {'$type': 'com.atproto.personalspace.policy'}

_NOTE = 'com.example.note'
_CAROL_DID = 'did:plc:carolcarolcarolcarolcaro'
_CAROL_PDS = 'https://carol.pds.test'
_UNKNOWN_DID = 'did:plc:unknownunknownunknownunk'
# CIDv1 of no bytes with the raw codec
_EMPTY_BLOB_CID = 'bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku'

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/mac.test.ts
_KEY_SHARE = 'did:key:zDnaExample'
_MAC_SPACE = 'at://did:example:space/space/app.bsky.group/test'
_MAC_URI = f'{_MAC_SPACE}/did:example:alice/app.bsky.feed.post/1'
_MAC_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
_MAC_COMMIT = {'ver': 1, 'space': _MAC_SPACE, 'repo': 'did:example:alice', 'rev': '3kbcq3p7ad400', 'data': b'\x01' * 32}
_COMMIT_REQUEST = 'mac=("atproto-space-commit";sf);keyid="did:key:zDnaExample";tag="atproto-space-commit"'
_COMMIT_PARAMS = '("atproto-space-commit";sf);keyid="did:key:zDnaExample";tag="atproto-space-commit"'
_COMMIT_HEADER = (
    'ver=1, repo="did:example:alice", space="at://did:example:space/space/app.bsky.group/test", '
    'rev="3kbcq3p7ad400", data=:AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE=:'
)
_COMMIT_BASE = f'"atproto-space-commit";sf: {_COMMIT_HEADER}\n"@signature-params": {_COMMIT_PARAMS}'
_RECORD_REQUEST = 'mac=("atproto-space-record";sf);keyid="did:key:zDnaExample";tag="atproto-space-record"'
_RECORD_PARAMS = '("atproto-space-record";sf);keyid="did:key:zDnaExample";tag="atproto-space-record"'
_RECORD_HEADER = f'uri="{_MAC_URI}", cid="{_MAC_CID}"'
_RECORD_BASE = f'"atproto-space-record";sf: {_RECORD_HEADER}\n"@signature-params": {_RECORD_PARAMS}'

_SHARED_SECRET = b'\x02' * 32
# upstream tests use a random secret, so the MAC is computed for the secret above
_COMMIT_MAC = '1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYc9M='

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/http-signature.test.ts
_CREDENTIAL_PARAMS = '("authorization" "atproto-space-audience");tag="atproto-space-credential"'

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/verify_repo_test.go#L145-L162
_INDIGO_REPO = 'did:web:author.example'
_INDIGO_PDS = 'https://author.example'
_INDIGO_SPACE = 'at://did:web:authority.example/space/com.example.space/skey'
_INDIGO_REV = '3mtwwsccuqy22'
_EMPTY_ARCHIVE = bytes.fromhex(
    '2a6c0100b701a6637265766d336d7477777363637571793232637665720164646174615820e5a00aa9991ac8a5ee3109844d84a55583'
    'bd20572ad3ffcd42792f3c36b183ad647265706f766469643a7765623a617574686f722e6578616d706c6565247479706572617470726f'
    '746f2d73706163652d7265706f657370616365783b61743a2f2f6469643a7765623a617574686f726974792e6578616d706c652f737061'
    '63652f636f6d2e6578616d706c652e73706163652f736b657900'
)

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/verify_repo_test.go#L31-L45
_INDIGO_RECORDS = [
    RepoRecord(
        'com.example.record',
        'aaaaaaaa',
        'bafyreieie2lcmcbq7m7q5g5t2crp5sszk5uzs4kyh4v7nxth5zuudgexhi',
        {'$type': 'com.example.record', 'value': 1},
    ),
    RepoRecord(
        'com.example.record',
        'b',
        'bafyreig3i7y3qv2wcrtatrwncps37yn23dvhbjvyzuimfgntgqnsyi4gqy',
        {'$type': 'com.example.record', 'value': 2},
    ),
    RepoRecord(
        'com.other.record',
        'a',
        'bafyreia7nqjuedqpg3ityibxpj6wwfi6a3sctc2iwgia44rqeluxaeluee',
        {'$type': 'com.example.record', 'value': 3},
    ),
]
# the test of indigo compares with a reference implementation, so the digest is computed
_INDIGO_DIGEST = bytes.fromhex('b1934b5f6c70bb67c202710a8c2d63e8d6b7029b468cff014babff34e8f1261c')

_Headers = t.Dict[str, str]


def _generate_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def _get(network: FakeSpaceNetwork, pds: str, nsid: str, params: _Headers, headers: _Headers) -> httpx.Response:
    with httpx.Client(transport=network.transport) as client:
        return client.get(f'{pds}/xrpc/{nsid}', params=params, headers=headers)


def _post(
    network: FakeSpaceNetwork, pds: str, nsid: str, body: t.Dict[str, t.Any], headers: t.Optional[_Headers] = None
) -> httpx.Response:
    with httpx.Client(transport=network.transport) as client:
        return client.post(f'{pds}/xrpc/{nsid}', json=body, headers=headers)


def _authorize(network: FakeSpaceNetwork, **body: t.Any) -> httpx.Response:
    return _post(network, AUTHORITY_PDS, _AUTHORIZE, {'space': SPACE, **body})


def _mint(network: FakeSpaceNetwork, key: ec.EllipticCurvePrivateKey, did: str = ALICE_DID) -> str:
    response = _authorize(
        network,
        credentialKey=private_key_to_did_key(key),
        delegationToken=network.create_delegation_token(did, SPACE),
    )
    credential: str = response.json()['credential']

    return credential


def _nsid(request: httpx.Request) -> str:
    return request.url.path[len('/xrpc/') :]


def _bearer(account: Account) -> _Headers:
    return {'authorization': f'Bearer {account.access_token}'}


def _present(token: str, audience: str, key: ec.EllipticCurvePrivateKey) -> _Headers:
    """Build the headers of a reader from strings, without the serializer of the SDK."""
    authorization = f'Atproto-Space-Credential {token}'
    signature_base = (
        f'"authorization": {authorization}\n'
        f'"atproto-space-audience": {audience}\n'
        f'"@signature-params": {_CREDENTIAL_PARAMS}'
    )
    signature = base64.b64encode(P256().sign(key, signature_base.encode())).decode('ascii')

    return {
        'authorization': authorization,
        'atproto-space-audience': audience,
        'signature-input': f'sig={_CREDENTIAL_PARAMS}',
        'signature': f'sig=:{signature}:',
    }


def _present_new(network: FakeSpaceNetwork, audience: str) -> _Headers:
    key = _generate_key()
    return _present(_mint(network, key), audience, key)


def _request_mac(network: FakeSpaceNetwork, repo: str, profile: str) -> t.Tuple[Encapsulation, _Headers]:
    kem_key = network.accounts[repo].kem_key
    assert kem_key is not None

    encapsulation = encapsulate(private_key_to_did_key(kem_key), b'atproto-mac')
    return encapsulation, {
        'accept-signature': f'mac=("{profile}";sf);keyid="{encapsulation.key_share}";tag="{profile}"'
    }


def _parse_commit(response: httpx.Response) -> 'models.ComAtprotoSpaceDefs.Commit':
    body: t.Dict[str, t.Any] = response.json()
    return get_or_create(body, models.ComAtprotoSpaceGetLatestCommit.Response).commit


def _parse_ops(response: httpx.Response) -> 'models.ComAtprotoSpaceListRepoOps.Response':
    body: t.Dict[str, t.Any] = response.json()
    return get_or_create(body, models.ComAtprotoSpaceListRepoOps.Response)


def _hmac(signature_base: str) -> str:
    return base64.b64encode(hmac.new(_SHARED_SECRET, signature_base.encode(), hashlib.sha256).digest()).decode('ascii')


def _change_audience(headers: _Headers) -> None:
    headers['atproto-space-audience'] = ALICE_DID


def _change_token(headers: _Headers) -> None:
    headers['authorization'] += 'A'


def _change_signature(headers: _Headers) -> None:
    signature = headers['signature']
    headers['signature'] = f'{signature[:5]}{"B" if signature[5] == "A" else "A"}{signature[6:]}'


def _remove_signature(headers: _Headers) -> None:
    del headers['signature']


def _put_note(network: FakeSpaceNetwork, repo: str, rkey: str, text: str = 'hello') -> str:
    return network.put_record(SPACE, repo, _NOTE, rkey, {'$type': _NOTE, 'text': text})


def test_repo_archive_of_an_empty_repo_is_the_static_archive() -> None:
    network = FakeSpaceNetwork()
    author = network.add_account(_INDIGO_REPO, _INDIGO_PDS)
    network.repos[(_INDIGO_SPACE, _INDIGO_REPO)] = Repo(rev=_INDIGO_REV)

    response = _get(network, _INDIGO_PDS, _GET_REPO, {'space': _INDIGO_SPACE, 'repo': _INDIGO_REPO}, _bearer(author))

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/vnd.dasl.star'
    assert response.content == _EMPTY_ARCHIVE


def test_repo_archive_of_three_records_is_verified() -> None:
    network = FakeSpaceNetwork()
    author = network.add_account(_INDIGO_REPO, _INDIGO_PDS)
    for record in reversed(_INDIGO_RECORDS):
        network.put_record(_INDIGO_SPACE, _INDIGO_REPO, record.collection, record.rkey, record.value)

    response = _get(network, _INDIGO_PDS, _GET_REPO, {'space': _INDIGO_SPACE, 'repo': _INDIGO_REPO}, _bearer(author))
    star, commit = read_repo_archive(response.content)
    verify_commit(commit, _INDIGO_SPACE, _INDIGO_REPO)

    assert [key for key, _ in STAR.from_bytes(response.content).pairs] == [
        b'com.example.record/aaaaaaaa',
        b'com.example.record/b',
        b'com.other.record/a',
    ]
    assert commit.data == _INDIGO_DIGEST
    assert verify_repo_archive_records(star, commit) == _INDIGO_RECORDS


def test_parse_mac_request() -> None:
    assert parse_mac_request(_COMMIT_REQUEST, 'atproto-space-commit') == MacRequest('mac', _KEY_SHARE, _COMMIT_PARAMS)
    assert parse_mac_request(_RECORD_REQUEST, 'atproto-space-record') == MacRequest('mac', _KEY_SHARE, _RECORD_PARAMS)


def test_parse_mac_request_finds_the_request_by_its_tag() -> None:
    accept_signature = f'other=("content-digest");tag="other", m={_COMMIT_PARAMS}'

    assert parse_mac_request(accept_signature, 'atproto-space-commit') == MacRequest('m', _KEY_SHARE, _COMMIT_PARAMS)


def test_parse_mac_request_without_the_tag_of_the_profile() -> None:
    assert parse_mac_request(None, 'atproto-space-commit') is None
    assert parse_mac_request(f'other=("content-digest");tag="other", {_RECORD_REQUEST}', 'atproto-space-commit') is None


def test_create_commit_mac_headers() -> None:
    mac_request = MacRequest('mac', _KEY_SHARE, _COMMIT_PARAMS)

    headers = create_commit_mac_headers(_MAC_COMMIT, mac_request, _SHARED_SECRET)

    assert headers == {
        'atproto-space-commit': _COMMIT_HEADER,
        'signature-input': _COMMIT_REQUEST,
        'signature': f'mac=:{_hmac(_COMMIT_BASE)}:',
    }
    assert headers['signature'] == f'mac=:{_COMMIT_MAC}:'


def test_create_commit_mac_headers_under_the_requested_label() -> None:
    mac_request = parse_mac_request(f'sig1={_COMMIT_PARAMS}', 'atproto-space-commit')
    assert mac_request is not None

    headers = create_commit_mac_headers(_MAC_COMMIT, mac_request, _SHARED_SECRET)

    assert headers['signature-input'] == f'sig1={_COMMIT_PARAMS}'
    assert headers['signature'] == f'sig1=:{_COMMIT_MAC}:'


def test_create_record_mac_headers() -> None:
    mac_request = MacRequest('mac', _KEY_SHARE, _RECORD_PARAMS)

    headers = create_record_mac_headers(_MAC_URI, _MAC_CID, mac_request, _SHARED_SECRET)

    assert headers == {
        'atproto-space-record': _RECORD_HEADER,
        'signature-input': _RECORD_REQUEST,
        'signature': f'mac=:{_hmac(_RECORD_BASE)}:',
    }


def test_credentialed_request_is_accepted() -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'a')

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, _present_new(network, BOB_DID))

    assert response.status_code == 200
    assert [record['rkey'] for record in response.json()['records']] == ['a']
    assert network.count(_AUTHORIZE) == 1
    assert network.statuses(_LIST_RECORDS) == [200]


@pytest.mark.parametrize(
    ('change', 'error'),
    [
        pytest.param(_change_audience, 'BadSpaceSignature', id='audience'),
        pytest.param(_change_token, 'BadJwtSignature', id='token'),
        pytest.param(_change_signature, 'BadSpaceSignature', id='signature'),
        pytest.param(_remove_signature, 'BadSpaceSignature', id='no-signature'),
    ],
)
def test_credentialed_request_is_refused_after_a_change(change: t.Callable[[_Headers], None], error: str) -> None:
    network = build_network()
    headers = _present_new(network, BOB_DID)
    change(headers)

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, headers)

    assert response.status_code == 401
    assert response.json()['error'] == error


def test_credentialed_request_is_refused_with_the_credential_of_another_key() -> None:
    network = build_network()
    key = _generate_key()
    headers = _present(_mint(network, key), BOB_DID, key)
    headers['authorization'] = f'Atproto-Space-Credential {_mint(network, _generate_key())}'

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, headers)

    assert response.status_code == 401
    assert response.json()['error'] == 'BadSpaceSignature'


def test_credentialed_request_is_refused_with_a_credential_that_the_authority_did_not_sign() -> None:
    network = build_network()
    key = _generate_key()
    token = build_space_credential(AUTHORITY_DID, SPACE, private_key_to_did_key(key))

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, _present(token, BOB_DID, key))

    assert response.status_code == 401
    assert response.json()['error'] == 'BadJwtSignature'


def test_credentialed_request_is_refused_for_another_audience() -> None:
    network = build_network()

    response = _get(
        network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, _present_new(network, ALICE_DID)
    )

    assert response.status_code == 401
    assert response.json()['error'] == 'BadSpaceAudience'


def test_credentialed_request_is_refused_for_another_space() -> None:
    network = build_network()
    other = f'at://{AUTHORITY_DID}/space/com.example.group/other'

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': other, 'repo': BOB_DID}, _present_new(network, BOB_DID))

    assert response.status_code == 400
    assert response.json()['error'] == 'InvalidCredential'


def test_credentialed_request_is_refused_by_the_pds_of_another_account() -> None:
    network = build_network()

    response = _get(
        network, ALICE_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, _present_new(network, BOB_DID)
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'RepoNotFound'


def test_revoked_credentials_are_refused() -> None:
    network = build_network()
    headers = _present_new(network, BOB_DID)
    network.revoke_credentials()

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, headers)
    renewed = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, _present_new(network, BOB_DID))

    assert response.status_code == 401
    assert response.json()['error'] == 'CredentialRevoked'
    assert renewed.status_code == 200
    assert len(network.credentials) == 2


def test_expired_credential_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    network = build_network()
    headers = _present_new(network, BOB_DID)
    expires_at = time.time() + network.credential_lifetime
    monkeypatch.setattr(time, 'time', lambda: expires_at + 1)

    response = _get(network, BOB_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': BOB_DID}, headers)

    assert response.status_code == 401
    assert response.json()['error'] == 'JwtExpired'


def test_account_reads_its_own_repo_with_its_token() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    cid = _put_note(network, ALICE_DID, 'a')

    response = _get(
        network,
        ALICE_PDS,
        _GET_RECORD,
        {'space': SPACE, 'repo': ALICE_DID, 'collection': _NOTE, 'rkey': 'a'},
        _bearer(alice),
    )

    assert response.status_code == 200
    assert response.json() == {
        'uri': f'{SPACE}/{ALICE_DID}/{_NOTE}/a',
        'cid': cid,
        'value': {'$type': _NOTE, 'text': 'hello'},
    }
    assert 'signature' not in response.headers


def test_account_does_not_read_the_repo_of_another_account_with_its_token() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    network.add_account(_CAROL_DID, ALICE_PDS)
    _put_note(network, BOB_DID, 'a')

    other_pds = _get(network, BOB_PDS, _GET_LATEST_COMMIT, {'space': SPACE, 'repo': BOB_DID}, _bearer(alice))
    same_pds = _get(
        network,
        ALICE_PDS,
        _GET_LATEST_COMMIT,
        {'space': SPACE, 'repo': _CAROL_DID},
        _bearer(alice),
    )

    assert (other_pds.status_code, other_pds.json()['error']) == (401, 'InvalidToken')
    assert (same_pds.status_code, same_pds.json()['error']) == (400, 'RepoNotFound')


def test_commit_mac_of_a_credentialed_request_is_verified() -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')

    response = _get(
        network,
        BOB_PDS,
        _GET_LATEST_COMMIT,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), **accept_signature},
    )
    commit = _parse_commit(response)

    verify_commit(commit, SPACE, BOB_DID)
    verify_commit_mac(commit, encapsulation, response.headers)
    assert commit.data == network.get_commit(SPACE, BOB_DID)['data']


def test_record_mac_of_a_credentialed_request_is_verified() -> None:
    network = build_network()
    cid = _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-record')

    response = _get(
        network,
        BOB_PDS,
        _GET_RECORD,
        {'space': SPACE, 'repo': BOB_DID, 'collection': _NOTE, 'rkey': 'a'},
        {**_present_new(network, BOB_DID), **accept_signature},
    )

    verify_record_mac(f'{SPACE}/{BOB_DID}/{_NOTE}/a', cid, encapsulation, response.headers)


def test_repo_archive_of_a_credentialed_request_carries_the_commit_mac() -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')

    response = _get(
        network,
        BOB_PDS,
        _GET_REPO,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), **accept_signature},
    )
    star, commit = read_repo_archive(response.content)

    verify_commit_mac(commit, encapsulation, response.headers)
    assert [record.rkey for record in verify_repo_archive_records(star, commit)] == ['a']


def test_credentialed_request_must_ask_for_a_mac() -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'a')

    response = _get(
        network, BOB_PDS, _GET_LATEST_COMMIT, {'space': SPACE, 'repo': BOB_DID}, _present_new(network, BOB_DID)
    )

    assert response.status_code == 400
    assert response.json() == {
        'error': 'InvalidSpaceMac',
        'message': 'A MAC must be requested with tag "atproto-space-commit"',
    }


@pytest.mark.parametrize(
    ('accept_signature', 'message'),
    [
        pytest.param('???', 'malformed Accept-Signature header', id='malformed'),
        pytest.param(f'a={_COMMIT_PARAMS}, b={_COMMIT_PARAMS}', 'more than one MAC requested', id='two-requests'),
        pytest.param(f'{_COMMIT_REQUEST};created=1700000000', 'unsupported MAC parameter: created', id='created'),
        pytest.param(f'{_COMMIT_REQUEST};alg="ecdsa-p256-sha256"', 'MAC algorithm must be hmac-sha256', id='alg'),
        pytest.param(
            'mac=("atproto-space-record";sf);keyid="did:key:zDnaExample";tag="atproto-space-commit"',
            'must cover exactly',
            id='another-header',
        ),
        pytest.param(
            'mac=("atproto-space-commit");keyid="did:key:zDnaExample";tag="atproto-space-commit"',
            'must cover exactly',
            id='no-sf',
        ),
        pytest.param(
            'mac=("atproto-space-commit";sf "authorization");keyid="did:key:zDnaExample";tag="atproto-space-commit"',
            'must cover exactly',
            id='additional-header',
        ),
        pytest.param(
            'mac=("atproto-space-commit";sf);tag="atproto-space-commit"', 'missing or malformed keyid', id='no-keyid'
        ),
        pytest.param(
            'mac=("atproto-space-commit";sf);keyid="key-1";tag="atproto-space-commit"',
            'missing or malformed keyid',
            id='keyid-not-did',
        ),
        pytest.param(_COMMIT_REQUEST, 'invalid KEM key', id='keyid-not-key'),
    ],
)
def test_mac_request_is_refused(accept_signature: str, message: str) -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'a')

    response = _get(
        network,
        BOB_PDS,
        _GET_LATEST_COMMIT,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), 'accept-signature': accept_signature},
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'InvalidSpaceMac'
    assert message in response.json()['message']


def test_dropped_mac() -> None:
    network = build_network()
    network.drop_mac = True
    _put_note(network, BOB_DID, 'a')
    _, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')

    response = _get(
        network,
        BOB_PDS,
        _GET_LATEST_COMMIT,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), **accept_signature},
    )

    assert response.status_code == 200
    assert not {'atproto-space-commit', 'signature-input', 'signature'} & set(response.headers)


def test_corrupt_mac() -> None:
    network = build_network()
    network.corrupt_mac = True
    _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')

    response = _get(
        network,
        BOB_PDS,
        _GET_LATEST_COMMIT,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), **accept_signature},
    )
    commit = _parse_commit(response)

    with pytest.raises(SpaceMacError, match='MAC does not match'):
        verify_commit_mac(commit, encapsulation, response.headers)


def test_authorize_space_sync_issues_a_credential_bound_to_the_key() -> None:
    network = build_network()
    key = _generate_key()
    _put_note(network, ALICE_DID, 'a')

    response = _authorize(
        network,
        credentialKey=private_key_to_did_key(key),
        delegationToken=network.create_delegation_token(BOB_DID, SPACE),
    )
    credential = SpaceCredential.parse(response.json()['credential'], key, response.json()['spaceRev'])

    assert response.status_code == 200
    assert credential.renew_at == pytest.approx(time.time() + 540, abs=5)
    assert credential.space_rev == network.spaces[SPACE].writers[ALICE_DID].space_rev
    assert network.credentials == [credential.token]
    assert 'authorization' not in network.requests_to(_AUTHORIZE)[0].headers


@pytest.mark.parametrize(
    ('did', 'status_code'),
    [
        pytest.param(AUTHORITY_DID, 200, id='authority'),
        pytest.param(ALICE_DID, 200, id='member'),
        pytest.param(_CAROL_DID, 400, id='stranger'),
    ],
)
def test_authorize_space_sync_admits_the_accounts_of_the_space(did: str, status_code: int) -> None:
    network = build_network()
    network.add_account(_CAROL_DID, _CAROL_PDS)

    response = _authorize(
        network,
        credentialKey=private_key_to_did_key(_generate_key()),
        delegationToken=network.create_delegation_token(did, SPACE),
    )

    assert response.status_code == status_code
    assert response.json().get('error') == (None if status_code == 200 else 'SpaceNotFound')


def test_authorize_space_sync_without_a_delegation_token_needs_a_public_space() -> None:
    network = build_network()
    credential_key = private_key_to_did_key(_generate_key())

    refused = _authorize(network, credentialKey=credential_key)
    network.spaces[SPACE].public = True
    admitted = _authorize(network, credentialKey=credential_key)

    assert (refused.status_code, refused.json()['error']) == (400, 'SpaceNotFound')
    assert admitted.status_code == 200


def test_authorize_space_sync_refuses_a_deleted_space() -> None:
    network = build_network()
    network.spaces[SPACE].deleted = True

    response = _authorize(
        network,
        credentialKey=private_key_to_did_key(_generate_key()),
        delegationToken=network.create_delegation_token(ALICE_DID, SPACE),
    )

    assert (response.status_code, response.json()['error']) == (400, 'SpaceDeleted')


def test_authorize_space_sync_refuses_a_delegation_token_twice() -> None:
    network = build_network()
    credential_key = private_key_to_did_key(_generate_key())
    delegation_token = network.create_delegation_token(ALICE_DID, SPACE)

    first = _authorize(network, credentialKey=credential_key, delegationToken=delegation_token)
    second = _authorize(network, credentialKey=credential_key, delegationToken=delegation_token)

    assert first.status_code == 200
    assert (second.status_code, second.json()['error']) == (400, 'InvalidDelegationToken')


def test_authorize_space_sync_refuses_a_delegation_token_that_the_account_did_not_sign() -> None:
    network = build_network()
    delegation_token = build_delegation_token(ALICE_DID, SPACE, f'{AUTHORITY_DID}#atproto_pds')

    response = _authorize(
        network, credentialKey=private_key_to_did_key(_generate_key()), delegationToken=delegation_token
    )

    assert (response.status_code, response.json()['error']) == (400, 'InvalidDelegationToken')


def test_authorize_space_sync_is_served_by_the_host_of_the_space_only() -> None:
    network = build_network()
    body = {
        'space': SPACE,
        'credentialKey': private_key_to_did_key(_generate_key()),
        'delegationToken': network.create_delegation_token(ALICE_DID, SPACE),
    }

    response = _post(network, ALICE_PDS, _AUTHORIZE, body)

    assert (response.status_code, response.json()['error']) == (400, 'SpaceNotFound')


def test_delegation_token_of_the_pds_of_the_account() -> None:
    network = build_network()
    client = fake_client(network, network.accounts[ALICE_DID])

    token = client.com.atproto.space.get_delegation_token(
        models.ComAtprotoSpaceGetDelegationToken.Params(space=SPACE)
    ).token
    response = _authorize(network, credentialKey=private_key_to_did_key(_generate_key()), delegationToken=token)

    assert response.status_code == 200
    assert network.requests_to(_GET_DELEGATION_TOKEN)[0].url.host == 'alice.pds.test'


def test_writers_are_listed_in_the_order_of_their_last_write() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, BOB_DID, 'a')
    _put_note(network, ALICE_DID, 'b')
    network.remove_writer(SPACE, BOB_DID)
    headers = _present_new(network, AUTHORITY_DID)

    first = _get(network, AUTHORITY_PDS, _LIST_WRITERS, {'space': SPACE, 'limit': '1'}, headers).json()
    second = _get(
        network, AUTHORITY_PDS, _LIST_WRITERS, {'space': SPACE, 'limit': '1', 'cursor': first['cursor']}, headers
    ).json()
    last = _get(network, AUTHORITY_PDS, _LIST_WRITERS, {'space': SPACE, 'cursor': second['cursor']}, headers).json()
    writers = get_or_create(
        {'repos': first['repos'] + second['repos']}, models.ComAtprotoSpaceListWriters.Response
    ).repos

    alice_commit = network.get_commit(SPACE, ALICE_DID)
    assert isinstance(writers[0], models.ComAtprotoSpaceDefs.RepoWrite)
    assert (writers[0].repo, writers[0].repo_rev, writers[0].data) == (
        ALICE_DID,
        alice_commit['rev'],
        alice_commit['data'],
    )
    assert isinstance(writers[1], models.ComAtprotoSpaceDefs.RepoRemoved)
    assert writers[1].repo == BOB_DID
    assert first['cursor'] == writers[0].space_rev < writers[1].space_rev == second['cursor']
    assert last == {'repos': []}


def test_writers_are_not_listed_for_the_token_of_an_account() -> None:
    network = build_network()

    response = _get(network, AUTHORITY_PDS, _LIST_WRITERS, {'space': SPACE}, _bearer(network.accounts[AUTHORITY_DID]))

    assert (response.status_code, response.json()['error']) == (401, 'MissingJwt')


def test_write_of_an_account_outside_the_space_is_not_reported_to_its_host() -> None:
    network = build_network()
    network.add_account(_CAROL_DID, _CAROL_PDS)

    _put_note(network, _CAROL_DID, 'a')

    assert (SPACE, _CAROL_DID) in network.repos
    assert network.spaces[SPACE].writers == {}


def test_records_are_listed_in_pages() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    for rkey in ('a', 'b', 'c'):
        _put_note(network, ALICE_DID, rkey)
    network.put_record(SPACE, ALICE_DID, 'com.example.task', 'a', {'$type': 'com.example.task', 'done': True})
    params = {'space': SPACE, 'repo': ALICE_DID, 'collection': _NOTE, 'limit': '2'}

    first = _get(network, ALICE_PDS, _LIST_RECORDS, params, _bearer(alice)).json()
    second = _get(
        network,
        ALICE_PDS,
        _LIST_RECORDS,
        {**params, 'cursor': first['cursor'], 'excludeValues': 'true'},
        _bearer(alice),
    ).json()
    malformed = _get(network, ALICE_PDS, _LIST_RECORDS, {**params, 'cursor': 'page2'}, _bearer(alice))

    assert [record['rkey'] for record in first['records']] == ['c', 'b']
    assert first['records'][0]['value'] == {'$type': _NOTE, 'text': 'hello'}
    assert first['cursor'] == f'{SPACE}/{ALICE_DID}/{_NOTE}/b'
    assert second == {'records': [{'collection': _NOTE, 'rkey': 'a', 'cid': first['records'][0]['cid']}]}
    assert (malformed.status_code, malformed.json()['error']) == (400, 'InvalidCursor')


def test_blobs_are_listed_and_served() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    _put_note(network, ALICE_DID, 'a')
    blobs = {network.add_blob(SPACE, ALICE_DID, data, 'image/png'): data for data in (b'', b'one', b'two')}
    cids = sorted(blobs)
    params = {'space': SPACE, 'repo': ALICE_DID}

    first = _get(network, ALICE_PDS, _LIST_BLOBS, {**params, 'limit': '2'}, _bearer(alice)).json()
    second = _get(network, ALICE_PDS, _LIST_BLOBS, {**params, 'cursor': first['cursor']}, _bearer(alice)).json()
    blob = _get(network, ALICE_PDS, _GET_BLOB, {**params, 'cid': cids[0]}, _present_new(network, ALICE_DID))
    missing = _get(network, ALICE_PDS, _GET_BLOB, {**params, 'cid': _MAC_CID}, _bearer(alice))

    assert _EMPTY_BLOB_CID in blobs
    assert first == {'cids': cids[:2], 'cursor': cids[1]}
    assert second == {'cids': cids[2:]}
    assert blob.content == blobs[cids[0]]
    assert blob.headers['content-type'] == 'image/png'
    assert (missing.status_code, missing.json()['error']) == (400, 'BlobNotFound')


def _list_ops(network: FakeSpaceNetwork, did: str, **params: str) -> t.Dict[str, t.Any]:
    response = _get(
        network,
        network.accounts[did].pds,
        _LIST_REPO_OPS,
        {'space': SPACE, 'repo': did, **params},
        _bearer(network.accounts[did]),
    )
    assert response.status_code == 200
    page: t.Dict[str, t.Any] = response.json()

    return page


def _list_all_ops(network: FakeSpaceNetwork, did: str, **params: str) -> t.List[t.Dict[str, t.Any]]:
    pages = [_list_ops(network, did, **params)]
    while 'cursor' in pages[-1]:
        pages.append(_list_ops(network, did, **params, cursor=pages[-1]['cursor']))

    return pages


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L146-L166
def test_operation_log_is_listed_in_pages_that_end_inside_of_a_commit() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    writes = [
        {'$type': 'com.atproto.space.applyWrites#create', 'collection': _NOTE, 'rkey': rkey, 'value': {'text': rkey}}
        for rkey in ('a', 'b', 'c', 'd', 'e')
    ]
    _post(network, ALICE_PDS, _APPLY_WRITES, {'space': SPACE, 'repo': ALICE_DID, 'writes': writes}, _bearer(alice))

    pages = _list_all_ops(network, ALICE_DID, limit='2')

    rev = network.repos[(SPACE, ALICE_DID)].rev
    assert [[op['rkey'] for op in page['ops']] for page in pages] == [['a', 'b'], ['c', 'd'], ['e']]
    assert [page.get('cursor') for page in pages] == [f'{rev}/1', f'{rev}/3', None]
    assert {op['rev'] for page in pages for op in page['ops']} == {rev}


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L168-L184
def test_operation_log_is_listed_after_a_revision() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'synced')
    since = network.repos[(SPACE, ALICE_DID)].rev
    for rkey in ('a', 'b', 'c'):
        _put_note(network, ALICE_DID, rkey)

    pages = _list_all_ops(network, ALICE_DID, since=since, limit='1')

    assert [op['rkey'] for page in pages for op in page['ops']] == ['a', 'b', 'c']
    assert [len(page['ops']) for page in pages] == [1, 1, 1, 0]


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L186-L207
def test_operation_log_replays_to_the_commit_that_every_page_carries_with_a_mac() -> None:
    network = build_network()
    _put_note(network, BOB_DID, 'one')
    _put_note(network, BOB_DID, 'two', 'first')
    _put_note(network, BOB_DID, 'two', 'revised')
    network.delete_record(SPACE, BOB_DID, _NOTE, 'one')
    credential = _present_new(network, BOB_DID)
    pages: t.List[models.ComAtprotoSpaceListRepoOps.Response] = []

    while not pages or pages[-1].cursor:
        params = {'space': SPACE, 'repo': BOB_DID, 'limit': '1'}
        if pages:
            params['cursor'] = t.cast('str', pages[-1].cursor)

        encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')
        response = _get(network, BOB_PDS, _LIST_REPO_OPS, params, {**credential, **accept_signature})
        page = _parse_ops(response)
        verify_commit(page.commit, SPACE, BOB_DID)
        verify_commit_mac(page.commit, encapsulation, response.headers)
        pages.append(page)

    ops = [op for page in pages for op in page.ops]
    replayed = RepoCommit()
    for op in ops:
        replayed.apply(op.collection, op.rkey, op.cid, op.prev)

    assert [(op.rkey, op.cid is None, op.prev is None) for op in ops] == [
        ('one', False, True),
        ('two', False, True),
        ('two', False, False),
        ('one', True, False),
    ]
    assert replayed.matches(pages[-1].commit)
    assert pages[-1].commit.data == network.get_commit(SPACE, BOB_DID)['data']


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L209-L228
def test_operation_is_listed_with_the_value_of_the_record_that_it_left_behind() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'self', 'first')
    _put_note(network, ALICE_DID, 'self', 'second')
    _put_note(network, ALICE_DID, 'gone')
    network.delete_record(SPACE, ALICE_DID, _NOTE, 'gone')

    ops = _list_ops(network, ALICE_DID)['ops']
    excluded = _list_ops(network, ALICE_DID, excludeValues='true')['ops']

    assert [op.get('value') for op in ops] == [None, {'$type': _NOTE, 'text': 'second'}, None, None]
    assert all(set(op) >= {'rev', 'collection', 'rkey', 'cid', 'prev'} for op in ops)
    assert [op for op in excluded if 'value' in op] == []
    assert [op['rkey'] for op in excluded] == ['self', 'self', 'gone', 'gone']


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L230-L238
@pytest.mark.parametrize('cursor', ['not-a-cursor', '3jzfcijpj2z2a/', '3jzfcijpj2z2a/x'])
def test_operation_log_refuses_a_malformed_cursor(cursor: str) -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    _put_note(network, ALICE_DID, 'a')

    response = _get(
        network, ALICE_PDS, _LIST_REPO_OPS, {'space': SPACE, 'repo': ALICE_DID, 'cursor': cursor}, _bearer(alice)
    )

    assert (response.status_code, response.json()['error']) == (400, 'InvalidCursor')


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/pds/tests/space/sync.test.ts#L344-L360
def test_operation_log_of_a_repo_that_was_not_written_to_is_not_found() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]

    response = _get(network, ALICE_PDS, _LIST_REPO_OPS, {'space': SPACE, 'repo': ALICE_DID}, _bearer(alice))

    assert (response.status_code, response.json()['error']) == (400, 'RepoNotFound')


def test_operation_log_is_cut_to_the_limit_of_the_host() -> None:
    network = build_network()
    network.ops_limit = 2
    for rkey in ('a', 'b', 'c'):
        _put_note(network, ALICE_DID, rkey)

    pages = _list_all_ops(network, ALICE_DID)

    assert [[op['rkey'] for op in page['ops']] for page in pages] == [['a', 'b'], ['c']]


def test_tampered_operation_log_carries_the_mac_of_the_commit_as_it_was() -> None:
    network = build_network()
    network.tamper_ops = lambda page: page['ops'][0].update(rkey='other')
    _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')

    response = _get(
        network,
        BOB_PDS,
        _LIST_REPO_OPS,
        {'space': SPACE, 'repo': BOB_DID},
        {**_present_new(network, BOB_DID), **accept_signature},
    )
    page = _parse_ops(response)

    verify_commit_mac(page.commit, encapsulation, response.headers)
    assert [op.rkey for op in page.ops] == ['other']
    assert [op.rkey for op in network.repos[(SPACE, BOB_DID)].ops] == ['a']


def test_tampered_commit_is_covered_by_the_mac() -> None:
    network = build_network()
    network.tamper_commit = lambda commit: commit.update(repo=ALICE_DID)
    _put_note(network, BOB_DID, 'a')
    encapsulation, accept_signature = _request_mac(network, BOB_DID, 'atproto-space-commit')
    headers = {**_present_new(network, BOB_DID), **accept_signature}
    params = {'space': SPACE, 'repo': BOB_DID}

    latest = _get(network, BOB_PDS, _GET_LATEST_COMMIT, params, headers)
    ops = _get(network, BOB_PDS, _LIST_REPO_OPS, params, headers)
    archive = _get(network, BOB_PDS, _GET_REPO, params, headers)

    commits = [_parse_commit(latest), _parse_ops(ops).commit, read_repo_archive(archive.content)[1]]
    assert [commit.repo for commit in commits] == [ALICE_DID] * 3
    for commit, response in zip(commits, [latest, ops, archive]):
        verify_commit_mac(commit, encapsulation, response.headers)
    assert network.get_commit(SPACE, BOB_DID)['repo'] == BOB_DID


def test_tampered_repo_archive_carries_the_commit_as_it_was() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    network.tamper_archive = lambda pairs: pairs.clear()
    _put_note(network, ALICE_DID, 'a')

    response = _get(network, ALICE_PDS, _GET_REPO, {'space': SPACE, 'repo': ALICE_DID}, _bearer(alice))
    star, commit = read_repo_archive(response.content)

    assert commit.data == network.get_commit(SPACE, ALICE_DID)['data']
    assert star.pairs == []
    with pytest.raises(SpaceRepoVerificationError, match='Records do not match the commit data'):
        verify_repo_archive_records(star, commit)


def test_repo_of_an_unavailable_account_is_served_to_the_account_only() -> None:
    network = build_network()
    bob = network.accounts[BOB_DID]
    bob.unavailable = 'RepoTakendown'
    _put_note(network, BOB_DID, 'a')
    params = {'space': SPACE, 'repo': BOB_DID}

    own = _get(network, BOB_PDS, _LIST_RECORDS, params, _bearer(bob))
    other = _get(network, BOB_PDS, _LIST_RECORDS, params, _present_new(network, BOB_DID))

    assert own.status_code == 200
    assert (other.status_code, other.json()['error']) == (400, 'RepoTakendown')


def test_write_routes_of_the_pds_of_the_account() -> None:
    network = build_network()
    client = fake_client(network, network.accounts[ALICE_DID])
    space = client.com.atproto.space

    created = space.create_record(
        models.ComAtprotoSpaceCreateRecord.Data(space=SPACE, repo=ALICE_DID, collection=_NOTE, record={'text': 'a'})
    )
    rkey = created.uri.rsplit('/', 1)[1]
    updated = space.put_record(
        models.ComAtprotoSpacePutRecord.Data(
            space=SPACE, repo=ALICE_DID, collection=_NOTE, rkey=rkey, record={'$type': _NOTE, 'text': 'b'}
        )
    )
    space.put_record(
        models.ComAtprotoSpacePutRecord.Data(
            space=SPACE, repo=ALICE_DID, collection=_NOTE, rkey='gone', record={'text': 'c'}, validate_=False
        )
    )
    space.delete_record(
        models.ComAtprotoSpaceDeleteRecord.Data(space=SPACE, repo=ALICE_DID, collection=_NOTE, rkey='gone')
    )
    space.delete_record(
        models.ComAtprotoSpaceDeleteRecord.Data(space=SPACE, repo=ALICE_DID, collection=_NOTE, rkey='gone')
    )

    repo = network.repos[(SPACE, ALICE_DID)]
    assert created.uri == f'{SPACE}/{ALICE_DID}/{_NOTE}/{rkey}'
    assert created.validation_status == 'unknown'
    assert updated.uri == created.uri
    assert updated.cid != created.cid
    assert {path: record.value for path, record in repo.records.items()} == {
        f'{_NOTE}/{rkey}': {'$type': _NOTE, 'text': 'b'}
    }
    assert [(op.rkey, op.cid, op.prev) for op in repo.ops] == [
        (rkey, created.cid, None),
        (rkey, updated.cid, created.cid),
        ('gone', repo.ops[2].cid, None),
        ('gone', None, repo.ops[2].cid),
    ]
    assert [op.rev for op in repo.ops] == sorted({op.rev for op in repo.ops})
    assert network.spaces[SPACE].writers[ALICE_DID].repo_rev == repo.rev == repo.ops[-1].rev


def test_apply_writes_of_the_pds_of_the_account() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, ALICE_DID, 'b')
    body = {
        'space': SPACE,
        'repo': ALICE_DID,
        'writes': [
            {'$type': 'com.atproto.space.applyWrites#create', 'collection': _NOTE, 'rkey': 'c', 'value': {'text': 'c'}},
            {'$type': 'com.atproto.space.applyWrites#update', 'collection': _NOTE, 'rkey': 'a', 'value': {'text': 'd'}},
            {'$type': 'com.atproto.space.applyWrites#delete', 'collection': _NOTE, 'rkey': 'b'},
        ],
    }

    response = _post(network, ALICE_PDS, _APPLY_WRITES, body, _bearer(alice))
    output: t.Dict[str, t.Any] = response.json()
    results = get_or_create(output, models.ComAtprotoSpaceApplyWrites.Response).results or []

    repo = network.repos[(SPACE, ALICE_DID)]
    assert [type(result) for result in results] == [
        models.ComAtprotoSpaceApplyWrites.CreateResult,
        models.ComAtprotoSpaceApplyWrites.UpdateResult,
        models.ComAtprotoSpaceApplyWrites.DeleteResult,
    ]
    assert output['results'][0]['uri'] == f'{SPACE}/{ALICE_DID}/{_NOTE}/c'
    assert output['results'][1]['cid'] == repo.records[f'{_NOTE}/a'].cid
    assert {path: record.value['text'] for path, record in repo.records.items()} == {
        f'{_NOTE}/a': 'd',
        f'{_NOTE}/c': 'c',
    }
    assert len({op.rev for op in repo.ops[-3:]}) == 1


@pytest.mark.parametrize(
    ('write', 'error'),
    [
        pytest.param(
            {'$type': 'com.atproto.space.applyWrites#create', 'rkey': 'a'}, 'RecordAlreadyExists', id='create'
        ),
        pytest.param({'$type': 'com.atproto.space.applyWrites#update', 'rkey': 'z'}, 'RecordNotFound', id='update'),
        pytest.param({'$type': 'com.atproto.space.applyWrites#delete', 'rkey': 'z'}, 'RecordNotFound', id='delete'),
        pytest.param({'$type': 'com.atproto.space.applyWrites#upsert', 'rkey': 'z'}, 'InvalidRequest', id='unknown'),
    ],
)
def test_apply_writes_applies_all_the_writes_or_none(write: t.Dict[str, str], error: str) -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    _put_note(network, ALICE_DID, 'a')
    commit = network.get_commit(SPACE, ALICE_DID)
    writes = [
        {'$type': 'com.atproto.space.applyWrites#create', 'collection': _NOTE, 'rkey': 'b', 'value': {'text': 'b'}},
        {'collection': _NOTE, 'value': {'text': 'c'}, **write},
    ]

    response = _post(
        network, ALICE_PDS, _APPLY_WRITES, {'space': SPACE, 'repo': ALICE_DID, 'writes': writes}, _bearer(alice)
    )

    assert (response.status_code, response.json()['error']) == (400, error)
    assert network.get_commit(SPACE, ALICE_DID) == commit


def test_clear_records_of_the_pds_of_the_account() -> None:
    network = build_network()
    client = fake_client(network, network.accounts[ALICE_DID])
    _put_note(network, ALICE_DID, 'a')
    _put_note(network, ALICE_DID, 'b')
    rev = network.repos[(SPACE, ALICE_DID)].rev

    client.com.atproto.space.clear_records(models.ComAtprotoSpaceClearRecords.Data(space=SPACE, repo=ALICE_DID))

    repo = network.repos[(SPACE, ALICE_DID)]
    assert repo.records == {}
    assert repo.ops == []
    assert repo.rev > rev
    # Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/lthash.test.ts
    assert network.get_commit(SPACE, ALICE_DID)['data'].hex() == (
        'e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad'
    )
    assert network.spaces[SPACE].writers[ALICE_DID].repo_rev == repo.rev


def test_write_routes_refuse_the_repo_of_another_account() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    body = {'space': SPACE, 'repo': BOB_DID, 'collection': _NOTE, 'record': {'text': 'a'}}

    forbidden = _post(network, ALICE_PDS, _CREATE_RECORD, body, _bearer(alice))
    mistyped = _post(
        network,
        ALICE_PDS,
        _CREATE_RECORD,
        {**body, 'repo': ALICE_DID, 'record': {'$type': 'com.example.task'}},
        _bearer(alice),
    )
    unknown = _post(network, ALICE_PDS, _CREATE_RECORD, {**body, 'repo': ALICE_DID, 'validate': True}, _bearer(alice))
    credentialed = _post(
        network, ALICE_PDS, _CREATE_RECORD, {**body, 'repo': ALICE_DID}, _present_new(network, ALICE_DID)
    )

    assert (forbidden.status_code, forbidden.json()['error']) == (403, 'Forbidden')
    assert (mistyped.status_code, mistyped.json()['error']) == (400, 'InvalidRequest')
    assert (unknown.status_code, unknown.json()['error']) == (400, 'InvalidRequest')
    assert (credentialed.status_code, credentialed.json()['error']) == (401, 'InvalidToken')
    assert (SPACE, ALICE_DID) not in network.repos


def test_space_is_created_by_the_pds_of_its_authority() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    body = {'spaceType': 'com.example.group', 'skey': 'new', 'policy': _PERSONALSPACE_POLICY}

    created = _post(network, ALICE_PDS, _CREATE_SPACE, body, _bearer(alice))
    repeated = _post(network, ALICE_PDS, _CREATE_SPACE, body, _bearer(alice))
    generated = _post(network, ALICE_PDS, _CREATE_SPACE, {**body, 'skey': None}, _bearer(alice))
    unsupported = _post(
        network,
        ALICE_PDS,
        _CREATE_SPACE,
        {**body, 'skey': 'other', 'policy': {'$type': 'com.example.policy'}},
        _bearer(alice),
    )
    anonymous = _post(network, ALICE_PDS, _CREATE_SPACE, {**body, 'skey': 'other'})

    uri = f'at://{ALICE_DID}/space/com.example.group/new'
    assert created.json() == {'space': uri}
    assert network.spaces[uri].policy == _PERSONALSPACE_POLICY
    assert network.spaces[uri].members == set()
    assert (repeated.status_code, repeated.json()['error']) == (400, 'SpaceAlreadyExists')
    assert generated.json()['space'].startswith(f'at://{ALICE_DID}/space/com.example.group/3')
    assert (unsupported.status_code, unsupported.json()['error']) == (400, 'UnsupportedPolicy')
    assert anonymous.status_code == 401
    assert len(network.spaces) == 3


def test_space_is_managed_by_its_authority_only() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    alice = network.accounts[ALICE_DID]
    unknown = f'at://{AUTHORITY_DID}/space/com.example.group/unknown'

    served = _get(network, AUTHORITY_PDS, _GET_SPACE, {'space': SPACE}, _bearer(authority))
    member = _get(network, ALICE_PDS, _GET_SPACE, {'space': SPACE}, _bearer(alice))
    elsewhere = _get(network, ALICE_PDS, _GET_SPACE, {'space': SPACE}, _bearer(authority))
    credentialed = _get(network, AUTHORITY_PDS, _GET_SPACE, {'space': SPACE}, _present_new(network, AUTHORITY_DID))
    missing = _get(network, AUTHORITY_PDS, _GET_SPACE, {'space': unknown}, _bearer(authority))
    removal = _post(network, ALICE_PDS, _REMOVE_MEMBERS, {'space': SPACE, 'dids': [BOB_DID]}, _bearer(alice))

    assert served.json() == {'space': SPACE, 'policy': _MEMBERSPACE_POLICY}
    assert (member.status_code, member.json()['error']) == (400, 'NotAuthorized')
    assert (elsewhere.status_code, elsewhere.json()['error']) == (401, 'InvalidToken')
    assert (credentialed.status_code, credentialed.json()['error']) == (401, 'InvalidToken')
    assert (missing.status_code, missing.json()['error']) == (400, 'SpaceNotFound')
    assert (removal.status_code, removal.json()['error']) == (400, 'NotAuthorized')
    assert network.spaces[SPACE].members == {ALICE_DID, BOB_DID}


def test_policy_of_another_type_keeps_nothing_of_the_previous_one() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    public = {**_MEMBERSPACE_POLICY, 'publicRead': True}

    same = _post(network, AUTHORITY_PDS, _UPDATE_SPACE, {'space': SPACE, 'policy': public}, _bearer(authority))
    members = set(network.spaces[SPACE].members)
    other = _post(
        network, AUTHORITY_PDS, _UPDATE_SPACE, {'space': SPACE, 'policy': _PERSONALSPACE_POLICY}, _bearer(authority)
    )
    listing = _get(network, AUTHORITY_PDS, _LIST_MEMBERS, {'space': SPACE}, _bearer(authority))

    assert (same.status_code, other.status_code) == (200, 200)
    assert members == {ALICE_DID, BOB_DID}
    assert network.spaces[SPACE].policy == _PERSONALSPACE_POLICY
    assert network.spaces[SPACE].members == set()
    assert (listing.status_code, listing.json()['error']) == (400, 'PolicyMismatch')


def test_deleted_space_takes_the_repo_of_its_authority_along() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    _put_note(network, AUTHORITY_DID, 'a')
    _put_note(network, ALICE_DID, 'a')

    deleted = _post(network, AUTHORITY_PDS, _DELETE_SPACE, {'space': SPACE}, _bearer(authority))
    repeated = _post(network, AUTHORITY_PDS, _DELETE_SPACE, {'space': SPACE}, _bearer(authority))
    lookup = _get(network, AUTHORITY_PDS, _GET_SPACE, {'space': SPACE}, _bearer(authority))

    assert (deleted.status_code, repeated.status_code) == (200, 200)
    assert network.spaces[SPACE].deleted
    assert list(network.repos) == [(SPACE, ALICE_DID)]
    assert (lookup.status_code, lookup.json()['error']) == (400, 'SpaceNotFound')


def test_writer_is_removed_by_the_authority_of_the_space() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    _put_note(network, ALICE_DID, 'a')
    body = {'space': SPACE, 'repo': ALICE_DID}

    removed = _post(network, AUTHORITY_PDS, _REMOVE_WRITER, body, _bearer(authority))
    space_rev = network.spaces[SPACE].writers[ALICE_DID].space_rev
    repeated = _post(network, AUTHORITY_PDS, _REMOVE_WRITER, body, _bearer(authority))
    absent = _post(network, AUTHORITY_PDS, _REMOVE_WRITER, {**body, 'repo': BOB_DID}, _bearer(authority))

    assert (removed.status_code, repeated.status_code, absent.status_code) == (200, 200, 200)
    assert network.spaces[SPACE].writers[ALICE_DID].removed
    assert network.spaces[SPACE].writers[ALICE_DID].space_rev == space_rev
    assert list(network.spaces[SPACE].writers) == [ALICE_DID]


def test_members_are_listed_in_the_order_of_their_dids() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    network.add_account(_CAROL_DID, _CAROL_PDS)
    members = [{'did': _CAROL_DID, 'read': True, 'write': False}, {'did': BOB_DID, 'read': False, 'write': False}]
    params = {'space': SPACE, 'limit': '2'}

    put = _post(network, AUTHORITY_PDS, _PUT_MEMBERS, {'space': SPACE, 'members': members}, _bearer(authority))
    first = _get(network, AUTHORITY_PDS, _LIST_MEMBERS, params, _bearer(authority))
    second = _get(network, AUTHORITY_PDS, _LIST_MEMBERS, {**params, 'cursor': BOB_DID}, _bearer(authority))
    last = _get(network, AUTHORITY_PDS, _LIST_MEMBERS, {**params, 'cursor': _CAROL_DID}, _bearer(authority))
    malformed = _get(network, AUTHORITY_PDS, _LIST_MEMBERS, {**params, 'cursor': 'first'}, _bearer(authority))

    assert put.status_code == 200
    assert first.json() == {
        'members': [{'did': ALICE_DID, 'read': True, 'write': True}, {'did': BOB_DID, 'read': False, 'write': False}],
        'cursor': BOB_DID,
    }
    assert second.json() == {'members': [{'did': _CAROL_DID, 'read': True, 'write': False}], 'cursor': _CAROL_DID}
    assert last.json() == {'members': []}
    assert (malformed.status_code, malformed.json()['error']) == (400, 'InvalidCursor')


@pytest.mark.parametrize(
    ('read', 'write'),
    [
        pytest.param(True, True, id='both'),
        pytest.param(True, False, id='read'),
        pytest.param(False, True, id='write'),
        pytest.param(False, False, id='neither'),
    ],
)
def test_member_reads_and_writes_the_space_as_its_access_lets_it(read: bool, write: bool) -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    member = {'did': ALICE_DID, 'read': read, 'write': write}

    _post(network, AUTHORITY_PDS, _PUT_MEMBERS, {'space': SPACE, 'members': [member]}, _bearer(authority))
    _put_note(network, ALICE_DID, 'a')
    credential = _authorize(
        network,
        credentialKey=private_key_to_did_key(_generate_key()),
        delegationToken=network.create_delegation_token(ALICE_DID, SPACE),
    )

    assert credential.status_code == (200 if read else 400)
    assert (ALICE_DID in network.spaces[SPACE].writers) == write


def test_removed_member_is_not_admitted() -> None:
    network = build_network()
    authority = network.accounts[AUTHORITY_DID]
    restricted = {'did': BOB_DID, 'read': True, 'write': False}
    _post(network, AUTHORITY_PDS, _PUT_MEMBERS, {'space': SPACE, 'members': [restricted]}, _bearer(authority))

    removed = _post(
        network,
        AUTHORITY_PDS,
        _REMOVE_MEMBERS,
        {'space': SPACE, 'dids': [ALICE_DID, BOB_DID, _CAROL_DID]},
        _bearer(authority),
    )
    credential = _authorize(
        network,
        credentialKey=private_key_to_did_key(_generate_key()),
        delegationToken=network.create_delegation_token(BOB_DID, SPACE),
    )

    assert removed.status_code == 200
    assert (credential.status_code, credential.json()['error']) == (400, 'SpaceNotFound')
    assert not network.spaces[SPACE].allows(ALICE_DID)
    assert network.spaces[SPACE].allows(AUTHORITY_DID, write=True)


def test_password_session_replaces_the_access_token_of_the_account() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    token = alice.access_token
    body = {'identifier': ALICE_DID, 'password': 'password'}

    wrong = _post(network, ALICE_PDS, _CREATE_SESSION, {**body, 'password': 'other'})
    elsewhere = _post(network, BOB_PDS, _CREATE_SESSION, body)
    session = _post(network, ALICE_PDS, _CREATE_SESSION, body).json()
    params = {'space': SPACE, 'repo': ALICE_DID}

    assert (wrong.status_code, elsewhere.status_code) == (401, 401)
    assert session['did'] == ALICE_DID
    assert session['accessJwt'] == alice.access_token != token
    assert _get(network, ALICE_PDS, _LIST_RECORDS, params, _bearer(alice)).status_code == 200
    assert _get(network, ALICE_PDS, _LIST_RECORDS, params, {'authorization': f'Bearer {token}'}).status_code == 401


def test_fake_password_client_reads_the_repo_of_its_account() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'a')
    alice = network.accounts[ALICE_DID]
    client = fake_password_client(network, alice)

    commit = client.com.atproto.space.get_latest_commit(
        models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=ALICE_DID)
    ).commit

    verify_commit(commit, SPACE, ALICE_DID)
    assert client.me is None
    assert network.log == [(ALICE_PDS, _CREATE_SESSION, 200), (ALICE_PDS, _GET_LATEST_COMMIT, 200)]
    assert network.requests_to(_GET_LATEST_COMMIT)[0].headers['authorization'] == f'Bearer {alice.access_token}'


@pytest.mark.asyncio
async def test_async_fake_password_client_reads_the_repo_of_its_account() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'a')
    alice = network.accounts[ALICE_DID]
    client = await async_fake_password_client(network, alice)

    commit = (
        await client.com.atproto.space.get_latest_commit(
            models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=ALICE_DID)
        )
    ).commit

    verify_commit(commit, SPACE, ALICE_DID)
    assert network.log == [(ALICE_PDS, _CREATE_SESSION, 200), (ALICE_PDS, _GET_LATEST_COMMIT, 200)]
    assert network.requests_to(_GET_LATEST_COMMIT)[0].headers['authorization'] == f'Bearer {alice.access_token}'


def test_forced_responses_are_served_in_turn() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    network.forced_responses[_LIST_RECORDS] = [
        httpx.Response(401, json={'error': 'AuthenticationRequired', 'message': 'Revoked'}),
        httpx.Response(200, json={'records': [], 'cursor': 'page2'}),
    ]
    params = {'space': SPACE, 'repo': ALICE_DID}

    responses = [_get(network, ALICE_PDS, _LIST_RECORDS, params, _bearer(alice)) for _ in range(3)]

    assert [response.status_code for response in responses] == [401, 200, 200]
    assert [response.json().get('cursor') for response in responses] == [None, 'page2', None]
    assert network.statuses(_LIST_RECORDS) == [401, 200, 200]
    assert network.log[0] == (ALICE_PDS, _LIST_RECORDS, 401)


def test_delayed_response() -> None:
    network = build_network()
    network.delays[_LIST_RECORDS] = 0.1
    started_at = time.monotonic()

    response = _get(
        network, ALICE_PDS, _LIST_RECORDS, {'space': SPACE, 'repo': ALICE_DID}, _bearer(network.accounts[ALICE_DID])
    )

    assert response.status_code == 200
    # the clock of some platforms is coarse
    assert time.monotonic() - started_at >= 0.05


def test_held_response_does_not_block_the_requests_of_other_threads() -> None:
    network = build_network()
    gate = threading.Event()
    network.gates[_LIST_RECORDS] = gate
    alice = network.accounts[ALICE_DID]
    _put_note(network, ALICE_DID, 'a')
    params = {'space': SPACE, 'repo': ALICE_DID}

    held = threading.Thread(target=_get, args=(network, ALICE_PDS, _LIST_RECORDS, params, _bearer(alice)))
    held.start()
    deadline = time.monotonic() + 10
    while not network.requests and time.monotonic() < deadline:
        time.sleep(0.001)

    assert network.requests
    _get(network, ALICE_PDS, _GET_LATEST_COMMIT, params, _bearer(alice))
    gate.set()
    held.join()

    assert network.log == [(ALICE_PDS, _GET_LATEST_COMMIT, 200), (ALICE_PDS, _LIST_RECORDS, 200)]


def test_unknown_method_is_not_implemented() -> None:
    network = build_network()

    response = _get(network, ALICE_PDS, 'com.atproto.space.exportSpaceMeta', {}, {})

    assert (response.status_code, response.json()['error']) == (501, 'MethodNotImplemented')


def test_fake_id_resolver() -> None:
    network = build_network()
    network.add_account(_CAROL_DID, _CAROL_PDS, has_kem_key=False)
    alice = network.accounts[ALICE_DID]
    resolver = FakeIdResolver(network)

    did_doc = resolver.did.ensure_resolve(ALICE_DID)
    resolver.did.ensure_resolve(ALICE_DID, force_refresh=True)

    assert did_doc.get_pds_endpoint() == ALICE_PDS
    assert did_doc.get_did_key() == private_key_to_did_key(alice.signing_key)
    assert did_doc.get_kem_key() == private_key_to_did_key(t.cast('ec.EllipticCurvePrivateKey', alice.kem_key))
    assert resolver.did.ensure_resolve(_CAROL_DID).get_kem_key() is None
    assert resolver.did.calls == [(ALICE_DID, False), (ALICE_DID, True), (_CAROL_DID, False)]
    alice.kem_method = ('Multikey', 'zabc')
    assert resolver.did.ensure_resolve(ALICE_DID).get_kem_key() == 'did:key:zabc'
    assert resolver.did.resolve(_UNKNOWN_DID) is None
    with pytest.raises(DidNotFoundError):
        resolver.did.ensure_resolve(_UNKNOWN_DID)


def test_fake_id_resolver_keeps_a_document_until_it_is_refreshed() -> None:
    network = build_network()
    alice = network.accounts[ALICE_DID]
    resolver = FakeIdResolver(network, cache=True)

    did_doc = resolver.did.ensure_resolve(ALICE_DID)
    alice.pds = _CAROL_PDS

    assert resolver.did.ensure_resolve(ALICE_DID) is did_doc
    assert resolver.did.ensure_resolve(ALICE_DID, force_refresh=True).get_pds_endpoint() == _CAROL_PDS
    assert resolver.did.ensure_resolve(ALICE_DID).get_pds_endpoint() == _CAROL_PDS
    assert resolver.did.calls == [(ALICE_DID, False), (ALICE_DID, False), (ALICE_DID, True), (ALICE_DID, False)]


def test_fake_client_reads_the_repo_of_its_account() -> None:
    network = build_network()
    _put_note(network, ALICE_DID, 'a')
    client = fake_client(network, network.accounts[ALICE_DID])

    commit = client.com.atproto.space.get_latest_commit(
        models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=ALICE_DID)
    ).commit

    verify_commit(commit, SPACE, ALICE_DID)
    assert commit.data == network.get_commit(SPACE, ALICE_DID)['data']
    assert network.requests_to(_GET_LATEST_COMMIT)[0].headers['authorization'].startswith('Bearer access-')


@pytest.mark.asyncio
async def test_async_fake_id_resolver() -> None:
    network = build_network()
    resolver = AsyncFakeIdResolver(network)

    did_doc = await resolver.did.ensure_resolve(BOB_DID, force_refresh=True)

    assert did_doc.get_pds_endpoint() == BOB_PDS
    assert resolver.did.calls == [(BOB_DID, True)]
    assert await resolver.did.resolve(_UNKNOWN_DID) is None
    with pytest.raises(DidNotFoundError):
        await resolver.did.ensure_resolve(_UNKNOWN_DID)


@pytest.mark.asyncio
async def test_async_fake_id_resolver_keeps_a_document_until_it_is_refreshed() -> None:
    network = build_network()
    bob = network.accounts[BOB_DID]
    resolver = AsyncFakeIdResolver(network, cache=True)

    did_doc = await resolver.did.ensure_resolve(BOB_DID)
    bob.pds = _CAROL_PDS

    assert await resolver.did.ensure_resolve(BOB_DID) is did_doc
    assert (await resolver.did.ensure_resolve(BOB_DID, force_refresh=True)).get_pds_endpoint() == _CAROL_PDS
    assert (await resolver.did.ensure_resolve(BOB_DID)).get_pds_endpoint() == _CAROL_PDS
    assert await resolver.did.resolve(_UNKNOWN_DID) is None


@pytest.mark.asyncio
async def test_async_fake_client_reads_the_repo_of_its_account() -> None:
    network = build_network()
    cid = _put_note(network, ALICE_DID, 'a')
    client = await async_fake_client(network, network.accounts[ALICE_DID])

    record = await client.com.atproto.space.get_record(
        models.ComAtprotoSpaceGetRecord.Params(space=SPACE, repo=ALICE_DID, collection=_NOTE, rkey='a')
    )

    assert record.cid == cid
    assert network.count(_GET_RECORD) == 1


@pytest.mark.asyncio
async def test_async_held_response_does_not_block_other_requests() -> None:
    network = build_network()
    gate = asyncio.Event()
    network.gates[_LIST_RECORDS] = gate
    _put_note(network, ALICE_DID, 'a')
    client = await async_fake_client(network, network.accounts[ALICE_DID])
    space = client.com.atproto.space

    async def get_latest_commit() -> None:
        await space.get_latest_commit(models.ComAtprotoSpaceGetLatestCommit.Params(space=SPACE, repo=ALICE_DID))
        gate.set()

    await asyncio.gather(
        space.list_records(models.ComAtprotoSpaceListRecords.Params(space=SPACE, repo=ALICE_DID)),
        get_latest_commit(),
    )

    assert [_nsid(request) for request in network.requests] == [_LIST_RECORDS, _GET_LATEST_COMMIT]
    assert network.log == [(ALICE_PDS, _GET_LATEST_COMMIT, 200), (ALICE_PDS, _LIST_RECORDS, 200)]
