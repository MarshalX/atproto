import json
import re
import time
import typing as t

import pytest
from atproto_crypto.algs import P256
from atproto_crypto.did import parse_did_key, private_key_to_did_key
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from atproto_crypto.jwk import base64url_decode, base64url_encode
from atproto_space.exceptions import SpaceTokenError
from atproto_space.tokens import (
    CLIENT_ATTESTATION_TYP,
    DELEGATION_TOKEN_TYP,
    SPACE_CREDENTIAL_MAX_AGE,
    SPACE_CREDENTIAL_TYP,
    SpaceTokenKind,
    create_client_attestation,
    get_space_host_audience,
    parse_space_token,
)
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.token_builder import build_delegation_token, build_space_credential, build_token

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/credential.test.ts
_SPACE = 'at://did:example:space/space/app.bsky.group/test'
_USER = 'did:example:alice'
_AUTHORITY = 'did:example:space'
_SPACE_HOST = 'did:example:space#atproto_pds'
_CLIENT_ID = 'https://app.example.com/client-metadata.json'

_CLIENT_KEY = ec.generate_private_key(ec.SECP256R1())
_HOLDER_KEY_ID = private_key_to_did_key(ec.generate_private_key(ec.SECP256R1()))

_NOW = int(time.time())


def _build(kind: SpaceTokenKind) -> str:
    if kind == 'delegation':
        return build_delegation_token(_USER, _SPACE, _SPACE_HOST)

    if kind == 'credential':
        return build_space_credential(_AUTHORITY, _SPACE, _HOLDER_KEY_ID)

    return create_client_attestation(_CLIENT_ID, _SPACE_HOST, _CLIENT_KEY, kid='key-1')


def _decode(token: str) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
    header, payload, _ = token.split('.')
    return json.loads(base64url_decode(header)), json.loads(base64url_decode(payload))


def _patch(part: t.Dict[str, t.Any], patch: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {name: value for name, value in {**part, **patch}.items() if value is not None}


def _tamper(token: str, header: t.Dict[str, t.Any], payload: t.Dict[str, t.Any]) -> str:
    """Rebuild the token with header and payload fields replaced, or removed when ``None``."""
    token_header, token_payload = _decode(token)
    return build_token(_patch(token_header, header), _patch(token_payload, payload))


def test_get_space_host_audience() -> None:
    assert get_space_host_audience(_AUTHORITY) == _SPACE_HOST


def test_parse_delegation_token() -> None:
    token = parse_space_token('delegation', _build('delegation'))

    assert token.iss == _USER
    assert token.sub == _SPACE
    assert token.aud == _SPACE_HOST
    assert token.iat is not None
    assert token.exp - token.iat == 60
    assert token.key_id is None


def test_parse_space_credential() -> None:
    token = parse_space_token('credential', _build('credential'))

    assert token.iss == _AUTHORITY
    assert token.sub == _SPACE
    assert token.aud is None
    assert token.key_id == _HOLDER_KEY_ID
    assert token.iat is not None
    assert token.exp - token.iat == 600
    assert re.fullmatch(r'[0-9a-f]{32}', token.jti)


def test_parse_space_credential_with_the_longest_lifetime() -> None:
    credential = build_space_credential(_AUTHORITY, _SPACE, _HOLDER_KEY_ID, expires_in=SPACE_CREDENTIAL_MAX_AGE)

    token = parse_space_token('credential', credential)

    assert token.iat is not None
    assert token.exp - token.iat == 3600


def test_client_attestation_names_the_client_id_as_iss_and_sub() -> None:
    attestation = _build('client_attestation')
    header, payload = _decode(attestation)

    assert header == {'alg': 'ES256', 'typ': CLIENT_ATTESTATION_TYP, 'kid': 'key-1'}
    assert set(payload) == {'iss', 'sub', 'aud', 'iat', 'exp', 'jti'}
    assert payload['exp'] - payload['iat'] == 60
    assert abs(payload['iat'] - time.time()) < 5
    assert re.fullmatch(r'[0-9a-f]{32}', payload['jti'])

    token = parse_space_token('client_attestation', attestation)

    assert token.iss == _CLIENT_ID
    assert token.sub == _CLIENT_ID
    assert token.aud == _SPACE_HOST


def test_client_attestation_is_signed_with_the_client_key() -> None:
    attestation = create_client_attestation(_CLIENT_ID, _SPACE_HOST, _CLIENT_KEY, expires_in=30)
    signing_input, signature = attestation.rsplit('.', 1)
    header, payload = _decode(attestation)

    assert header == {'alg': 'ES256', 'typ': CLIENT_ATTESTATION_TYP}
    assert payload['exp'] - payload['iat'] == 30
    assert P256().verify_signature(
        parse_did_key(private_key_to_did_key(_CLIENT_KEY)).key_bytes,
        signing_input.encode(),
        base64url_decode(signature),
    )


def test_create_client_attestation_refuses_a_key_that_is_not_p256() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        create_client_attestation(_CLIENT_ID, _SPACE_HOST, ec.generate_private_key(ec.SECP256K1()))


def test_every_client_attestation_is_unique() -> None:
    jtis = {_decode(_build('client_attestation'))[1]['jti'] for _ in range(20)}

    assert len(jtis) == 20


@pytest.mark.parametrize(
    ('kind', 'header', 'payload', 'code', 'message'),
    [
        ('credential', {'typ': DELEGATION_TOKEN_TYP}, {}, 'BadJwtType', 'Wrong token type'),
        ('credential', {'alg': None}, {}, 'BadJwt', 'Missing token "alg"'),
        ('credential', {'kid': '#other'}, {}, 'BadJwt', 'Wrong token "kid"'),
        ('credential', {}, {'iss': None}, 'BadJwtIss', 'Missing token "iss"'),
        ('credential', {}, {'sub': None}, 'BadJwtSub', 'Missing token "sub"'),
        ('credential', {}, {'exp': None}, 'BadJwt', 'Missing token "exp"'),
        ('delegation', {}, {'exp': True}, 'BadJwt', 'Missing token "exp"'),
        ('credential', {}, {'jti': None}, 'BadJwt', 'Missing token "jti"'),
        ('delegation', {}, {'aud': None}, 'BadJwtAudience', 'Missing token "aud"'),
        ('client_attestation', {}, {'aud': None}, 'BadJwtAudience', 'Missing token "aud"'),
        ('credential', {}, {'cnf': None}, 'BadJwtCnf', 'Missing token "cnf.kid"'),
        ('credential', {}, {'cnf': {'kid': 'key-1'}}, 'BadJwtCnf', 'Missing token "cnf.kid"'),
        ('credential', {}, {'iat': None}, 'BadJwt', 'Invalid space credential lifetime'),
        ('credential', {}, {'iat': _NOW, 'exp': _NOW + 3601}, 'BadJwt', 'Invalid space credential lifetime'),
        (
            'client_attestation',
            {},
            {'sub': 'https://other.example/client-metadata.json'},
            'BadJwtIss',
            'must both be the client ID',
        ),
    ],
    ids=[
        'a token of another type',
        'a token with no alg',
        'a kid other than #atproto',
        'a token with no iss',
        'a token with no sub',
        'a token with no exp',
        'a delegation token whose exp is a boolean',
        'a token with no jti',
        'a delegation token with no aud',
        'a client attestation with no aud',
        'a credential with no cnf',
        'a credential whose cnf.kid is not a DID',
        'a credential with no iat',
        'a credential lasting over 60 minutes',
        'a client attestation whose sub is not its iss',
    ],
)
def test_parse_space_token_rejects(
    kind: SpaceTokenKind, header: t.Dict[str, t.Any], payload: t.Dict[str, t.Any], code: str, message: str
) -> None:
    token = _tamper(_build(kind), header, payload)

    with pytest.raises(SpaceTokenError, match=message) as exc_info:
        parse_space_token(kind, token)

    assert exc_info.value.code == code


@pytest.mark.parametrize(
    ('token', 'message'),
    [
        ('nope', 'expected 3 parts'),
        ('!!!.e30.c2ln', 'Could not parse token header'),
        ('e30.!!!.c2ln', 'Could not parse token payload'),
        ('W10.e30.c2ln', 'Could not parse token header'),
        ('e30.bnVsbA.c2ln', 'Could not parse token payload'),
        ('ééé.e30.c2ln', 'Could not parse token header'),
        (f'e30.{base64url_encode(b"[" * 100_000)}.c2ln', 'Could not parse token payload'),
        ('e3\n\n\n\n0.e30.c2ln', 'Could not parse token header'),
        ('e30.e3\n\n\n\n0.c2ln', 'Could not parse token payload'),
        ('e30.e30=.c2ln', 'Could not parse token payload'),
        ('e30.e30.', 'Could not parse token signature'),
        ('e30.e30.c2ln\n"atproto-space-audience": did:example:other', 'Could not parse token signature'),
        ('e30.e30.c2 ln', 'Could not parse token signature'),
        ('e30.e30.c2lné', 'Could not parse token signature'),
        ('e30.e30.c2ln=', 'Could not parse token signature'),
    ],
    ids=[
        'a string that is not a JWT',
        'a header that is not base64url JSON',
        'a payload that is not base64url JSON',
        'a header that is not an object',
        'a payload that is not an object',
        'a header that is not ASCII',
        'a payload that is nested too deep',
        'a header with line breaks',
        'a payload with line breaks',
        'a payload with padding',
        'a token with no signature',
        'a signature with a line break',
        'a signature with a space',
        'a signature that is not ASCII',
        'a signature with padding',
    ],
)
def test_parse_space_token_rejects_malformed_jwt(token: str, message: str) -> None:
    with pytest.raises(SpaceTokenError, match=message) as exc_info:
        parse_space_token('credential', token)

    assert exc_info.value.code == 'BadJwt'


@pytest.mark.parametrize(
    'payload',
    [
        {'iat': _NOW, 'exp': _NOW},
        {'iat': _NOW + 600, 'exp': _NOW},
        {'iat': str(_NOW)},
        {'iat': False, 'exp': 600},
        {'exp': str(_NOW + 600)},
        {'exp': float('nan')},
        {'exp': float('inf')},
        {'exp': 10**400},
        {'iss': 1},
        {'sub': ''},
        {'jti': 1},
        {'cnf': 'did:key:zDnaExample'},
        {'cnf': {'kid': 'did:key:zDnaExample\n'}},
        {'cnf': {'kid': f'did:key:{"z" * 2048}'}},
    ],
)
def test_parse_space_credential_rejects_invalid_claims(payload: t.Dict[str, t.Any]) -> None:
    token = _tamper(_build('credential'), {}, payload)

    with pytest.raises(SpaceTokenError):
        parse_space_token('credential', token)


def test_parse_space_token_does_not_require_a_kid_of_a_client_attestation() -> None:
    attestation = create_client_attestation(_CLIENT_ID, _SPACE_HOST, _CLIENT_KEY)

    assert parse_space_token('client_attestation', attestation).iss == _CLIENT_ID


def test_token_types() -> None:
    assert DELEGATION_TOKEN_TYP == 'atproto-space-delegation+jwt'
    assert SPACE_CREDENTIAL_TYP == 'atproto-space-credential+jwt'
    assert CLIENT_ATTESTATION_TYP == 'atproto-client-attestation+jwt'
