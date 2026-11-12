import json
import typing as t

from cryptography.hazmat.primitives.asymmetric import ec

from atproto_crypto.algs.p256 import P256
from atproto_crypto.consts import P256_JWT_ALG
from atproto_crypto.jwk import base64url_encode

_P256: t.Final = P256()


def _encode_segment(segment: t.Mapping[str, t.Any]) -> str:
    return base64url_encode(json.dumps(segment, separators=(',', ':')).encode('utf-8'))


def sign_jwt(
    header: t.Mapping[str, t.Any], payload: t.Mapping[str, t.Any], private_key: ec.EllipticCurvePrivateKey
) -> str:
    """Sign a JWT with ES256.

    Args:
        header: JOSE header. ``alg`` is set to ``ES256``.
        payload: Claims.
        private_key: P-256 private key.

    Returns:
        :obj:`str`: JWT in the compact serialization.
    """
    signing_input = f'{_encode_segment({**header, "alg": P256_JWT_ALG})}.{_encode_segment(payload)}'
    signature = _P256.sign(private_key, signing_input.encode('ascii'))

    return f'{signing_input}.{base64url_encode(signature)}'
