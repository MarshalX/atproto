import json

from atproto_crypto.algs import P256
from atproto_crypto.consts import P256_CURVE_ORDER
from atproto_crypto.jwk import base64url_decode
from atproto_crypto.jws import sign_jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature


def test_sign_returns_low_s_signatures_accepted_by_verifier() -> None:
    alg = P256()
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )

    for i in range(64):
        signing_input = f'message-{i}'.encode()
        signature = alg.sign(private_key, signing_input)

        assert len(signature) == 64
        assert int.from_bytes(signature[32:], 'big') <= P256_CURVE_ORDER // 2
        assert alg.verify_signature(public_key, signing_input, signature)


def test_sign_jwt_is_a_valid_es256_compact_jws() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())

    jwt = sign_jwt({'typ': 'dpop+jwt', 'alg': 'none'}, {'jti': 'abc', 'iat': 1}, private_key)
    header, payload, signature = jwt.split('.')

    assert '=' not in jwt
    assert json.loads(base64url_decode(header)) == {'typ': 'dpop+jwt', 'alg': 'ES256'}
    assert json.loads(base64url_decode(payload)) == {'jti': 'abc', 'iat': 1}

    raw = base64url_decode(signature)
    der = encode_dss_signature(int.from_bytes(raw[:32], 'big'), int.from_bytes(raw[32:], 'big'))
    # raises on an invalid signature
    private_key.public_key().verify(der, f'{header}.{payload}'.encode(), ec.ECDSA(hashes.SHA256()))
