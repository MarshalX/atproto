import base64
import re

import pytest
from atproto_crypto.algs import P256
from atproto_crypto.did import parse_did_key, private_key_to_did_key
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from atproto_space.http_signature import build_signature_base, create_credential_headers
from cryptography.hazmat.primitives.asymmetric import ec

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/http-signature.test.ts
_TOKEN = 'credential'
_AUTHORIZATION = 'Atproto-Space-Credential credential'
_AUDIENCE = 'did:example:repo'
_SIGNATURE_PARAMS = '("authorization" "atproto-space-audience");tag="atproto-space-credential"'
_SIGNATURE_BASE = (
    f'"authorization": {_AUTHORIZATION}\n'
    f'"atproto-space-audience": {_AUDIENCE}\n'
    f'"@signature-params": {_SIGNATURE_PARAMS}'
).encode()

_KEY = ec.generate_private_key(ec.SECP256R1())


def _get_signature(header: str) -> bytes:
    return base64.b64decode(header[len('sig=:') : -1], validate=True)


def test_create_credential_headers() -> None:
    headers = create_credential_headers(_TOKEN, _AUDIENCE, _KEY)

    assert set(headers) == {'authorization', 'atproto-space-audience', 'signature-input', 'signature'}
    assert headers['authorization'] == _AUTHORIZATION
    assert headers['atproto-space-audience'] == _AUDIENCE
    assert headers['signature-input'] == f'sig={_SIGNATURE_PARAMS}'
    assert re.fullmatch(r'sig=:[A-Za-z0-9+/]+=*:', headers['signature'])


def test_create_credential_headers_signs_the_signature_base() -> None:
    headers = create_credential_headers(_TOKEN, _AUDIENCE, _KEY)
    signature = _get_signature(headers['signature'])
    public_key = parse_did_key(private_key_to_did_key(_KEY)).key_bytes

    assert len(signature) == 64
    assert P256().verify_signature(public_key, _SIGNATURE_BASE, signature)
    assert not P256().verify_signature(public_key, _SIGNATURE_BASE + b'\n', signature)


def test_create_credential_headers_binds_the_audience() -> None:
    headers = create_credential_headers(_TOKEN, 'did:example:other', _KEY)
    public_key = parse_did_key(private_key_to_did_key(_KEY)).key_bytes

    assert not P256().verify_signature(public_key, _SIGNATURE_BASE, _get_signature(headers['signature']))


def test_create_credential_headers_refuses_a_key_that_is_not_p256() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        create_credential_headers(_TOKEN, _AUDIENCE, ec.generate_private_key(ec.SECP256K1()))


def test_build_signature_base() -> None:
    signature_base = build_signature_base(
        ['"authorization"', '"atproto-space-audience"'], [_AUTHORIZATION, _AUDIENCE], _SIGNATURE_PARAMS
    )

    assert signature_base == _SIGNATURE_BASE


def test_build_signature_base_ignores_whitespace_around_values() -> None:
    signature_base = build_signature_base(
        ['"authorization"', '"atproto-space-audience"'], [f' {_AUTHORIZATION}  ', f'{_AUDIENCE}\t'], _SIGNATURE_PARAMS
    )

    assert signature_base == _SIGNATURE_BASE


def test_build_signature_base_of_a_structured_field() -> None:
    # Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/mac.test.ts
    covered = 'ver=1, rev="3kbcq3p7ad400"'
    signature_params = '("atproto-space-commit";sf);keyid="did:key:zDnaExample";tag="atproto-space-commit"'

    signature_base = build_signature_base(['"atproto-space-commit";sf'], [covered], signature_params)

    assert signature_base == f'"atproto-space-commit";sf: {covered}\n"@signature-params": {signature_params}'.encode()
