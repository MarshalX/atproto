import base64
import hashlib
import json
import typing as t

from cryptography.hazmat.primitives.asymmetric import ec

from atproto_crypto.exceptions import InvalidJwkError

Jwk = t.Dict[str, t.Any]

_P256_CRV: t.Final = 'P-256'
_COORDINATE_SIZE: t.Final = 32
_PRIVATE_MEMBERS: t.Final = frozenset({'d', 'p', 'q', 'dp', 'dq', 'qi', 'oth', 'k'})


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def base64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))


def _encode_coordinate(value: int) -> str:
    return base64url_encode(value.to_bytes(_COORDINATE_SIZE, 'big'))


def _decode_coordinate(jwk: t.Mapping[str, t.Any], name: str) -> int:
    value = jwk.get(name)
    if not isinstance(value, str):
        raise InvalidJwkError(f'JWK member "{name}" is missing')

    try:
        decoded = base64url_decode(value)
    except ValueError as e:
        raise InvalidJwkError(f'JWK member "{name}" is not base64url') from e

    if len(decoded) != _COORDINATE_SIZE:
        raise InvalidJwkError(f'JWK member "{name}" must be {_COORDINATE_SIZE} bytes')

    return int.from_bytes(decoded, 'big')


def _ensure_p256(jwk: t.Mapping[str, t.Any]) -> None:
    if jwk.get('kty') != 'EC' or jwk.get('crv') != _P256_CRV:
        raise InvalidJwkError('Only EC keys on the P-256 curve are supported')


def private_key_to_jwk(private_key: ec.EllipticCurvePrivateKey, kid: t.Optional[str] = None) -> Jwk:
    """Export a P-256 private key as a private JWK.

    Args:
        private_key: P-256 private key.
        kid: Key ID to put into the JWK.

    Returns:
        :obj:`dict`: Private JWK.
    """
    if not isinstance(private_key.curve, ec.SECP256R1):
        raise InvalidJwkError('Only EC keys on the P-256 curve are supported')

    numbers = private_key.private_numbers()
    jwk: Jwk = {
        'kty': 'EC',
        'crv': _P256_CRV,
        'x': _encode_coordinate(numbers.public_numbers.x),
        'y': _encode_coordinate(numbers.public_numbers.y),
        'd': _encode_coordinate(numbers.private_value),
    }
    if kid is not None:
        jwk['kid'] = kid

    return jwk


def generate_p256_jwk(kid: t.Optional[str] = None) -> Jwk:
    """Generate a P-256 key.

    Args:
        kid: Key ID to put into the JWK.

    Returns:
        :obj:`dict`: Private JWK.
    """
    return private_key_to_jwk(ec.generate_private_key(ec.SECP256R1()), kid)


def get_public_jwk(jwk: t.Mapping[str, t.Any]) -> Jwk:
    """Return the JWK without its private members."""
    _ensure_p256(jwk)
    return {name: value for name, value in jwk.items() if name not in _PRIVATE_MEMBERS}


def load_private_jwk(jwk: t.Mapping[str, t.Any]) -> ec.EllipticCurvePrivateKey:
    """Load a P-256 private key from a private JWK.

    Raises:
        :class:`atproto_crypto.exceptions.InvalidJwkError`: The JWK is not a P-256 private key.
    """
    _ensure_p256(jwk)
    public_numbers = ec.EllipticCurvePublicNumbers(
        _decode_coordinate(jwk, 'x'), _decode_coordinate(jwk, 'y'), ec.SECP256R1()
    )
    try:
        return ec.EllipticCurvePrivateNumbers(_decode_coordinate(jwk, 'd'), public_numbers).private_key()
    except ValueError as e:
        raise InvalidJwkError('JWK is not a valid P-256 private key') from e


def load_public_jwk(jwk: t.Mapping[str, t.Any]) -> ec.EllipticCurvePublicKey:
    """Load a P-256 public key from a JWK.

    Raises:
        :class:`atproto_crypto.exceptions.InvalidJwkError`: The JWK is not a P-256 key.
    """
    _ensure_p256(jwk)
    try:
        return ec.EllipticCurvePublicNumbers(
            _decode_coordinate(jwk, 'x'), _decode_coordinate(jwk, 'y'), ec.SECP256R1()
        ).public_key()
    except ValueError as e:
        raise InvalidJwkError('JWK is not a valid P-256 public key') from e


def get_jwk_thumbprint(jwk: t.Mapping[str, t.Any]) -> str:
    """Compute the SHA-256 thumbprint of a P-256 JWK as defined by RFC 7638."""
    _ensure_p256(jwk)
    members = {'crv': jwk['crv'], 'kty': jwk['kty'], 'x': jwk.get('x'), 'y': jwk.get('y')}
    if not isinstance(members['x'], str) or not isinstance(members['y'], str):
        raise InvalidJwkError('JWK members "x" and "y" are required')

    canonical = json.dumps(members, separators=(',', ':'), sort_keys=True)
    return base64url_encode(hashlib.sha256(canonical.encode('utf-8')).digest())
