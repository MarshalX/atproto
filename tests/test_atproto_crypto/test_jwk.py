import typing as t

import pytest
from atproto_crypto.exceptions import InvalidJwkError
from atproto_crypto.jwk import (
    generate_p256_jwk,
    get_jwk_thumbprint,
    get_public_jwk,
    load_private_jwk,
    load_public_jwk,
    private_key_to_jwk,
)
from cryptography.hazmat.primitives.asymmetric import ec

# RFC 9449, section 6.1
_RFC9449_JWK = {
    'kty': 'EC',
    'crv': 'P-256',
    'x': 'l8tFrhx-34tV3hRICRDY9zCkDlpBhF42UQUfWVAWBFs',
    'y': '9VE4jf_Ok_o64zbTTlcuNJajHmt6v9TDVrU0CdvGRDA',
}
_RFC9449_JKT = '0ZcOCORZNYy-DWpqq30jZyJGHTN0d2HglBV3uiguA4I'


def test_thumbprint_matches_rfc_vector() -> None:
    assert get_jwk_thumbprint(_RFC9449_JWK) == _RFC9449_JKT


def test_thumbprint_ignores_optional_members() -> None:
    assert get_jwk_thumbprint({**_RFC9449_JWK, 'kid': 'key-1', 'use': 'sig'}) == _RFC9449_JKT


def test_generated_jwk_round_trips() -> None:
    jwk = generate_p256_jwk(kid='key-1')
    assert jwk['kid'] == 'key-1'
    assert {len(jwk[name]) for name in ('x', 'y', 'd')} == {43}

    private_key = load_private_jwk(jwk)
    assert private_key_to_jwk(private_key, kid='key-1') == jwk


def test_public_jwk_has_no_private_members() -> None:
    jwk = generate_p256_jwk(kid='key-1')
    public_jwk = get_public_jwk(jwk)

    assert 'd' not in public_jwk
    assert public_jwk['kid'] == 'key-1'
    assert load_public_jwk(public_jwk).public_numbers() == load_private_jwk(jwk).public_key().public_numbers()


def test_coordinates_are_left_padded() -> None:
    # a private value that needs padding to 32 bytes
    private_key = ec.derive_private_key(1, ec.SECP256R1())
    jwk = private_key_to_jwk(private_key)

    assert len(jwk['d']) == 43
    assert load_private_jwk(jwk).private_numbers().private_value == 1


@pytest.mark.parametrize(
    'jwk',
    [
        {'kty': 'RSA', 'n': 'AQAB', 'e': 'AQAB'},
        {'kty': 'EC', 'crv': 'secp256k1', 'x': 'AA', 'y': 'AA', 'd': 'AA'},
        {'kty': 'EC', 'crv': 'P-256', 'x': 'AA', 'y': 'AA', 'd': 'AA'},
        {**_RFC9449_JWK},
        {**_RFC9449_JWK, 'd': '!!!'},
    ],
)
def test_load_private_jwk_rejects_invalid(jwk: t.Dict[str, t.Any]) -> None:
    with pytest.raises(InvalidJwkError):
        load_private_jwk(jwk)


def test_private_key_to_jwk_rejects_other_curves() -> None:
    with pytest.raises(InvalidJwkError):
        private_key_to_jwk(ec.generate_private_key(ec.SECP256K1()))
