import hashlib
import time

import pytest
from atproto_crypto.jwk import base64url_encode, generate_p256_jwk, get_jwk_thumbprint
from atproto_oauth.dpop import (
    DpopKey,
    NonceCache,
    build_dpop_proof,
    generate_nonce,
    get_htu,
    is_auth_server_nonce_error,
    is_invalid_token_error,
    is_resource_server_nonce_error,
)
from atproto_oauth.pkce import generate_pkce, get_pkce_challenge

from tests.test_atproto_oauth.fake_server import decode_jwt, verify_jwt


def test_proof_for_the_authorization_server() -> None:
    jwk = generate_p256_jwk(kid='ignored')
    key = DpopKey(jwk)

    proof = build_dpop_proof(key, 'post', 'https://auth.test/oauth/token')
    header, payload = decode_jwt(proof)

    assert header == {'typ': 'dpop+jwt', 'alg': 'ES256', 'jwk': key.public_jwk}
    assert set(header['jwk']) == {'kty', 'crv', 'x', 'y'}
    assert get_jwk_thumbprint(header['jwk']) == get_jwk_thumbprint(jwk)
    assert verify_jwt(proof, header['jwk'])

    assert set(payload) == {'jti', 'htm', 'htu', 'iat'}
    assert payload['htm'] == 'POST'
    assert payload['htu'] == 'https://auth.test/oauth/token'
    assert abs(payload['iat'] - time.time()) < 5


def test_proof_for_the_resource_server() -> None:
    key = DpopKey(generate_p256_jwk())

    proof = build_dpop_proof(
        key, 'GET', 'https://pds.test/xrpc/app.bsky.feed.getTimeline?limit=1#top', 'nonce-1', 'access-token'
    )
    _, payload = decode_jwt(proof)

    assert payload['htu'] == 'https://pds.test/xrpc/app.bsky.feed.getTimeline'
    assert payload['nonce'] == 'nonce-1'
    assert payload['ath'] == base64url_encode(hashlib.sha256(b'access-token').digest())


def test_every_proof_is_unique() -> None:
    key = DpopKey(generate_p256_jwk())
    jtis = {decode_jwt(build_dpop_proof(key, 'GET', 'https://pds.test/xrpc/x'))[1]['jti'] for _ in range(50)}

    assert len(jtis) == 50


@pytest.mark.parametrize(
    ('url', 'htu'),
    [
        ('https://pds.test/xrpc/x?a=1&b=2', 'https://pds.test/xrpc/x'),
        ('https://pds.test/xrpc/x#frag', 'https://pds.test/xrpc/x'),
        ('https://pds.test:8443/xrpc/x', 'https://pds.test:8443/xrpc/x'),
        ('https://pds.test', 'https://pds.test'),
    ],
)
def test_htu(url: str, htu: str) -> None:
    assert get_htu(url) == htu


def test_nonce_errors_are_recognized() -> None:
    assert is_auth_server_nonce_error(400, {'error': 'use_dpop_nonce'})
    assert not is_auth_server_nonce_error(401, {'error': 'use_dpop_nonce'})
    assert not is_auth_server_nonce_error(400, {'error': 'invalid_grant'})
    assert not is_auth_server_nonce_error(400, None)
    assert not is_auth_server_nonce_error(400, ['use_dpop_nonce'])

    assert is_resource_server_nonce_error(401, 'DPoP error="use_dpop_nonce", error_description="nonce"')
    assert is_resource_server_nonce_error(401, 'DPoP algs="ES256", error="use_dpop_nonce"')
    assert not is_resource_server_nonce_error(400, 'DPoP error="use_dpop_nonce"')
    assert not is_resource_server_nonce_error(401, 'Bearer error="use_dpop_nonce"')
    assert not is_resource_server_nonce_error(401, 'DPoP error="invalid_token"')
    assert not is_resource_server_nonce_error(401, None)


def test_invalid_token_errors_are_recognized() -> None:
    assert is_invalid_token_error(401, 'DPoP error="invalid_token", error_description="expired"')
    assert is_invalid_token_error(401, 'Bearer error="invalid_token"')
    assert not is_invalid_token_error(403, 'DPoP error="invalid_token"')
    assert not is_invalid_token_error(401, 'DPoP error="use_dpop_nonce"')
    assert not is_invalid_token_error(401, 'DPoP error_description="mentions error=\\"invalid_token\\""')
    assert not is_invalid_token_error(401, None)


def test_nonce_cache() -> None:
    cache = NonceCache()
    assert cache.get('https://pds.test') is None

    cache.update('https://pds.test', None)
    assert cache.get('https://pds.test') is None

    cache.update('https://pds.test', 'nonce-1')
    cache.update('https://auth.test', 'nonce-2')
    cache.update('https://pds.test', '')
    assert cache.get('https://pds.test') == 'nonce-1'
    assert cache.get('https://auth.test') == 'nonce-2'


def test_pkce() -> None:
    # RFC 7636, appendix B
    assert (
        get_pkce_challenge('dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk')
        == 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM'
    )

    verifier, challenge = generate_pkce()
    assert len(verifier) == 43
    assert challenge == get_pkce_challenge(verifier)
    assert generate_pkce()[0] != verifier

    with pytest.raises(ValueError, match='32 to 96'):
        generate_pkce(16)


def test_nonce_is_url_safe_and_random() -> None:
    assert len({generate_nonce() for _ in range(50)}) == 50
    assert len(generate_nonce()) == 22
