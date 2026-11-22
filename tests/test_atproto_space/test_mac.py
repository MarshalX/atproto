import base64
import hashlib
import hmac
import typing as t

import pytest
from atproto_client import models
from atproto_crypto.did import private_key_to_did_key
from atproto_crypto.kem import Encapsulation, decapsulate, encapsulate
from atproto_space.exceptions import SpaceMacError
from atproto_space.mac import (
    COMMIT_MAC_PROFILE,
    MAC_KEM_INFO,
    RECORD_MAC_PROFILE,
    format_mac_request,
    verify_commit_mac,
    verify_record_mac,
)
from cryptography.hazmat.primitives.asymmetric import ec

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/mac.test.ts
_KEY_SHARE = 'did:key:zDnaExample'
_SPACE = 'at://did:example:space/space/app.bsky.group/test'
_URI = f'{_SPACE}/did:example:alice/app.bsky.feed.post/1'
_CID_A = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
_CID_B = 'bafyreidpw4cbv6gr4ukh33z23pvvrpr3wi4gnpmi4doamlsl3sa4rgri2a'

_COMMIT = models.ComAtprotoSpaceDefs.Commit(
    ver=1, space=_SPACE, repo='did:example:alice', rev='3kbcq3p7ad400', data=b'\x01' * 32
)
_COMMIT_HEADER = (
    f'ver=1, repo="did:example:alice", space="{_SPACE}", rev="3kbcq3p7ad400", '
    'data=:AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE=:'
)
_COMMIT_PARAMS = f'("atproto-space-commit";sf);keyid="{_KEY_SHARE}";tag="atproto-space-commit"'
_RECORD_HEADER = f'uri="{_URI}", cid="{_CID_A}"'
_RECORD_PARAMS = f'("atproto-space-record";sf);keyid="{_KEY_SHARE}";tag="atproto-space-record"'

_SHARED_SECRET = b'\x02' * 32
_ENCAPSULATION = Encapsulation(key_share=_KEY_SHARE, shared_secret=_SHARED_SECRET)
# upstream tests use a random secret, so the MAC is computed for the secret above
_COMMIT_MAC = '1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYc9M='

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/mac_test.go#L37-L91
_INDIGO_KEY_SHARE = 'did:key:test-request-key'
_INDIGO_SPACE = 'at://did:web:authority.example/space/com.example.space/skey'
_INDIGO_COMMIT = models.ComAtprotoSpaceDefs.Commit(
    ver=1, space=_INDIGO_SPACE, repo='did:web:author.example', rev='3mtwwsccuqy22', data=bytes(32)
)
_INDIGO_HEADER = (
    f'ver=1, repo="did:web:author.example", space="{_INDIGO_SPACE}", rev="3mtwwsccuqy22", '
    'data=:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=:'
)
_INDIGO_PARAMS = '("atproto-space-commit";sf);tag="atproto-space-commit"'
_INDIGO_ENCAPSULATION = Encapsulation(key_share=_INDIGO_KEY_SHARE, shared_secret=bytes([1, 2, 3]) + bytes(29))

_Headers = t.Dict[str, str]
_Mutation = t.Callable[[_Headers], None]


def _sign(profile: str, covered: str, params: str, secret: bytes = _SHARED_SECRET, label: str = 'mac') -> _Headers:
    """Build the headers of a host from strings, without the serializer of the SDK."""
    signature_base = f'"{profile}";sf: {covered}\n"@signature-params": {params}'.encode()
    mac = base64.b64encode(hmac.new(secret, signature_base, hashlib.sha256).digest()).decode('ascii')

    return {profile: covered, 'signature-input': f'{label}={params}', 'signature': f'{label}=:{mac}:'}


def _sign_commit(params: str = _COMMIT_PARAMS, covered: str = _COMMIT_HEADER) -> _Headers:
    return _sign(COMMIT_MAC_PROFILE, covered, params)


def _sign_indigo_commit(params: str, mutation: t.Optional[_Mutation]) -> _Headers:
    headers = _sign(
        COMMIT_MAC_PROFILE, _INDIGO_HEADER, params, secret=_INDIGO_ENCAPSULATION.shared_secret, label='renamed'
    )
    if mutation:
        mutation(headers)

    return headers


def _normalize_commit_header(headers: _Headers) -> None:
    headers['atproto-space-commit'] = _INDIGO_HEADER.replace(', ', ',')


def _change_commit_header(headers: _Headers) -> None:
    headers['atproto-space-commit'] = _INDIGO_HEADER.replace('ver=1', 'ver=2')


def _remove_commit_header(headers: _Headers) -> None:
    del headers['atproto-space-commit']


def _remove_signature(headers: _Headers) -> None:
    del headers['signature']


def _add_unrelated_signature(headers: _Headers) -> None:
    # a header that is sent more than once reaches the SDK as one value joined by a comma
    headers['signature-input'] += ', other=("date");tag="another-protocol"'
    headers['signature'] += ', other=:AA==:'


def _add_matching_signature(headers: _Headers) -> None:
    headers['signature-input'] += f', second={_INDIGO_PARAMS}'


def test_format_mac_request() -> None:
    assert format_mac_request(COMMIT_MAC_PROFILE, _KEY_SHARE) == (
        'mac=("atproto-space-commit";sf);keyid="did:key:zDnaExample";tag="atproto-space-commit"'
    )
    assert format_mac_request(RECORD_MAC_PROFILE, _KEY_SHARE) == (
        'mac=("atproto-space-record";sf);keyid="did:key:zDnaExample";tag="atproto-space-record"'
    )


def test_verify_commit_mac() -> None:
    headers = {
        'atproto-space-commit': _COMMIT_HEADER,
        'signature-input': f'sig1={_COMMIT_PARAMS}',
        'signature': f'sig1=:{_COMMIT_MAC}:',
    }

    verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)


def test_signer_of_tests_reproduces_commit_mac() -> None:
    headers = _sign(COMMIT_MAC_PROFILE, _COMMIT_HEADER, _COMMIT_PARAMS, label='sig1')

    assert headers['signature'] == f'sig1=:{_COMMIT_MAC}:'


def test_verify_commit_mac_with_encapsulated_shared_secret() -> None:
    kem_key = ec.generate_private_key(ec.SECP256R1())
    encapsulation = encapsulate(private_key_to_did_key(kem_key), MAC_KEM_INFO)
    params = format_mac_request(COMMIT_MAC_PROFILE, encapsulation.key_share)[len('mac=') :]

    shared_secret = decapsulate(kem_key, encapsulation.key_share, MAC_KEM_INFO)
    headers = _sign(COMMIT_MAC_PROFILE, _COMMIT_HEADER, params, secret=shared_secret)

    verify_commit_mac(_COMMIT, encapsulation, headers)


def test_mac_kem_info_derives_shared_secret_of_mac() -> None:
    # Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/mac_test.go#L15-L34
    sender = ec.derive_private_key(3, ec.SECP256R1())
    recipient = ec.derive_private_key(7, ec.SECP256R1())

    shared_secret = decapsulate(recipient, private_key_to_did_key(sender), MAC_KEM_INFO)

    assert shared_secret.hex() == '6d5583f6c99086921a36ba07358a13195fd4a1da7beb30eff853f05691108baf'


def test_verify_commit_mac_rejects_mac_under_another_shared_secret() -> None:
    headers = _sign(COMMIT_MAC_PROFILE, _COMMIT_HEADER, _COMMIT_PARAMS, secret=b'\x03' * 32)

    with pytest.raises(SpaceMacError, match='MAC does not match'):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)


@pytest.mark.parametrize(
    'field',
    [
        {'ver': 2},
        {'repo': 'did:example:bob'},
        {'space': f'{_SPACE}2'},
        {'rev': '3kbcq3p7ad401'},
        {'data': b'\x02' * 32},
    ],
)
def test_verify_commit_mac_rejects_another_commit(field: t.Dict[str, t.Any]) -> None:
    with pytest.raises(SpaceMacError, match='Commit does not match its MAC'):
        verify_commit_mac(_COMMIT.model_copy(update=field), _ENCAPSULATION, _sign_commit())


def test_verify_commit_mac_rejects_tampered_header() -> None:
    headers = _sign_commit()
    headers['atproto-space-commit'] = _COMMIT_HEADER.replace('3kbcq3p7ad400', '3kbcq3p7ad401')

    with pytest.raises(SpaceMacError, match='MAC does not match'):
        verify_commit_mac(_COMMIT.model_copy(update={'rev': '3kbcq3p7ad401'}), _ENCAPSULATION, headers)


def test_verify_commit_mac_ignores_insignificant_whitespace() -> None:
    headers = _sign_commit()
    headers['atproto-space-commit'] = _COMMIT_HEADER.replace(', ', ',   ')

    verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            f'("atproto-space-commit";sf);tag="atproto-space-commit";created=1700000000;keyid="{_KEY_SHARE}"',
            id='parameters added and reordered',
        ),
        pytest.param('("atproto-space-commit";sf);tag="atproto-space-commit"', id='no keyid'),
        pytest.param(f'{_COMMIT_PARAMS};alg="hmac-sha256"', id='an hmac-sha256 alg'),
    ],
)
def test_verify_commit_mac_accepts_other_parameters(params: str) -> None:
    verify_commit_mac(_COMMIT, _ENCAPSULATION, _sign_commit(params))


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        pytest.param(
            '("atproto-space-commit";sf);keyid="did:key:zDnaOther";tag="atproto-space-commit"',
            'keyid does not match',
            id='another keyid',
        ),
        pytest.param(f'{_COMMIT_PARAMS};alg="hmac-sha512"', 'algorithm must be hmac-sha256', id='another alg'),
        pytest.param(f'{_COMMIT_PARAMS};alg=hmac-sha256', 'algorithm must be hmac-sha256', id='alg as a token'),
        pytest.param(
            f'("atproto-space-commit");keyid="{_KEY_SHARE}";tag="atproto-space-commit"',
            'must cover exactly',
            id='the header not flagged sf',
        ),
        pytest.param(
            f'("atproto-space-commit";sf=1);keyid="{_KEY_SHARE}";tag="atproto-space-commit"',
            'must cover exactly',
            id='sf as an integer',
        ),
        pytest.param(
            f'("atproto-space-commit";sf);keyid="{_KEY_SHARE}";tag=atproto-space-commit',
            'Missing signature input with tag',
            id='tag as a token',
        ),
    ],
)
def test_verify_commit_mac_rejects_other_requirements(params: str, message: str) -> None:
    with pytest.raises(SpaceMacError, match=message):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, _sign_commit(params))


@pytest.mark.parametrize(
    ('header', 'message'),
    [
        ('atproto-space-commit', 'Missing atproto-space-commit header'),
        ('signature', 'Missing signature header'),
        ('signature-input', 'Missing signature-input header'),
    ],
)
def test_verify_commit_mac_rejects_response_without_header(header: str, message: str) -> None:
    headers = _sign_commit()
    del headers[header]

    with pytest.raises(SpaceMacError, match=message):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)


@pytest.mark.parametrize(
    ('header', 'value', 'message'),
    [
        ('atproto-space-commit', '???', 'Malformed atproto-space-commit header'),
        ('signature-input', '???', 'Malformed signature-input header'),
        ('signature', '???', 'Malformed signature header'),
        ('signature', 'mac="1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYc9M="', 'Missing or malformed signature'),
        ('signature', f'mac=:{_COMMIT_MAC}:;created=1700000000', 'Missing or malformed signature'),
        ('signature', f'mac=(:{_COMMIT_MAC}:)', 'Missing or malformed signature'),
        ('signature', f'other=:{_COMMIT_MAC}:', 'Missing or malformed signature'),
        ('signature', 'mac=:1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYc9A=:', 'MAC does not match'),
        ('signature', 'mac=:1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYcw==:', 'MAC does not match'),
        ('signature', 'mac=::', 'MAC does not match'),
    ],
)
def test_verify_commit_mac_rejects_malformed_header(header: str, value: str, message: str) -> None:
    headers = _sign_commit()
    headers[header] = value

    with pytest.raises(SpaceMacError, match=message):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)


@pytest.mark.parametrize(
    'covered',
    [
        pytest.param(_COMMIT_HEADER.replace('ver=1', 'ver'), id='ver as a boolean'),
        pytest.param(_COMMIT_HEADER.replace('ver=1', 'ver=1.0'), id='ver as a decimal'),
        pytest.param(_COMMIT_HEADER.replace('ver=1', 'ver="1"'), id='ver as a string'),
        pytest.param(_COMMIT_HEADER.replace('ver=1', 'ver=(1)'), id='ver as an inner list'),
        pytest.param(_COMMIT_HEADER.replace('ver=1, ', ''), id='no ver'),
        pytest.param(_COMMIT_HEADER.replace('"did:example:alice"', 'did:example:alice'), id='repo as a token'),
        pytest.param(_COMMIT_HEADER.replace('data=:', 'data="').replace('=:', '="'), id='data as a string'),
        pytest.param('', id='no fields'),
    ],
)
def test_verify_commit_mac_rejects_header_of_another_shape(covered: str) -> None:
    with pytest.raises(SpaceMacError, match='Commit does not match its MAC'):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, _sign_commit(covered=covered))


@pytest.mark.parametrize(
    ('params', 'mutation'),
    [
        pytest.param(_INDIGO_PARAMS, None, id='arbitrary label'),
        pytest.param(f'{_INDIGO_PARAMS};keyid="{_INDIGO_KEY_SHARE}"', None, id='matching keyid'),
        pytest.param(f'{_INDIGO_PARAMS};alg="hmac-sha256"', None, id='explicit algorithm'),
        pytest.param(f'{_INDIGO_PARAMS};created=100;expires=200', None, id='other parameters are signed'),
        pytest.param(_INDIGO_PARAMS, _normalize_commit_header, id='normalized dictionary'),
        pytest.param(_INDIGO_PARAMS, _add_unrelated_signature, id='unrelated signatures'),
    ],
)
def test_verify_commit_mac_accepts_signature_profile(params: str, mutation: t.Optional[_Mutation]) -> None:
    verify_commit_mac(_INDIGO_COMMIT, _INDIGO_ENCAPSULATION, _sign_indigo_commit(params, mutation))


@pytest.mark.parametrize(
    ('params', 'mutation', 'message'),
    [
        pytest.param(f'{_INDIGO_PARAMS};keyid="other"', None, 'keyid does not match', id='wrong keyid'),
        pytest.param(
            f'{_INDIGO_PARAMS};alg="ecdsa-p256-sha256"', None, 'algorithm must be hmac-sha256', id='wrong algorithm'
        ),
        pytest.param(
            '("atproto-space-commit");tag="atproto-space-commit"', None, 'must cover exactly', id='missing sf'
        ),
        pytest.param(
            '("atproto-space-commit";sf=?0);tag="atproto-space-commit"', None, 'must cover exactly', id='false sf'
        ),
        pytest.param(
            '("atproto-space-commit";sf;req);tag="atproto-space-commit"',
            None,
            'must cover exactly',
            id='extra component parameter',
        ),
        pytest.param('("date";sf);tag="atproto-space-commit"', None, 'must cover exactly', id='wrong covered header'),
        pytest.param(
            '("atproto-space-commit";sf "date");tag="atproto-space-commit"',
            None,
            'must cover exactly',
            id='extra component',
        ),
        pytest.param(
            '("atproto-space-commit";sf);tag="atproto-space-record"',
            None,
            'Missing signature input with tag',
            id='wrong tag',
        ),
        pytest.param('("atproto-space-commit";sf)', None, 'Missing signature input with tag', id='missing tag'),
        pytest.param(
            _INDIGO_PARAMS, _add_matching_signature, 'More than one signature with tag', id='two matching signatures'
        ),
        pytest.param(_INDIGO_PARAMS, _remove_signature, 'Missing signature header', id='missing signature'),
        pytest.param(
            _INDIGO_PARAMS, _remove_commit_header, 'Missing atproto-space-commit header', id='missing covered header'
        ),
        pytest.param(_INDIGO_PARAMS, _change_commit_header, 'MAC does not match', id='changed covered value'),
    ],
)
def test_verify_commit_mac_rejects_signature_profile(
    params: str, mutation: t.Optional[_Mutation], message: str
) -> None:
    with pytest.raises(SpaceMacError, match=message):
        verify_commit_mac(_INDIGO_COMMIT, _INDIGO_ENCAPSULATION, _sign_indigo_commit(params, mutation))


def test_verify_record_mac() -> None:
    headers = _sign(RECORD_MAC_PROFILE, _RECORD_HEADER, _RECORD_PARAMS)

    verify_record_mac(_URI, _CID_A, _ENCAPSULATION, headers)

    assert headers['atproto-space-record'] == (
        'uri="at://did:example:space/space/app.bsky.group/test/did:example:alice/app.bsky.feed.post/1", '
        'cid="bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244"'
    )


@pytest.mark.parametrize(('uri', 'cid'), [(f'{_URI}2', _CID_A), (_URI, _CID_B)])
def test_verify_record_mac_rejects_another_record(uri: str, cid: str) -> None:
    headers = _sign(RECORD_MAC_PROFILE, _RECORD_HEADER, _RECORD_PARAMS)

    with pytest.raises(SpaceMacError, match='Record does not match its MAC'):
        verify_record_mac(uri, cid, _ENCAPSULATION, headers)


def test_verify_record_mac_rejects_mac_under_another_shared_secret() -> None:
    headers = _sign(RECORD_MAC_PROFILE, _RECORD_HEADER, _RECORD_PARAMS, secret=b'\x03' * 32)

    with pytest.raises(SpaceMacError, match='MAC does not match'):
        verify_record_mac(_URI, _CID_A, _ENCAPSULATION, headers)


def test_record_mac_is_not_accepted_as_commit_mac() -> None:
    headers = _sign(RECORD_MAC_PROFILE, _RECORD_HEADER, _RECORD_PARAMS)

    with pytest.raises(SpaceMacError, match='Missing signature input with tag "atproto-space-commit"'):
        verify_commit_mac(_COMMIT, _ENCAPSULATION, headers)
