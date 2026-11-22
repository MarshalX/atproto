import json
import math
import re
import secrets
import time
import typing as t
from dataclasses import dataclass

import typing_extensions as te
from atproto_core.uri.space import is_did
from atproto_crypto.consts import P256_JWT_ALG
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from atproto_crypto.jwk import base64url_decode
from atproto_crypto.jws import sign_jwt
from cryptography.hazmat.primitives.asymmetric import ec

from atproto_space.exceptions import SpaceTokenError

DELEGATION_TOKEN_TYP: t.Final = 'atproto-space-delegation+jwt'  # noqa: S105
SPACE_CREDENTIAL_TYP: t.Final = 'atproto-space-credential+jwt'
CLIENT_ATTESTATION_TYP: t.Final = 'atproto-client-attestation+jwt'

SPACE_CREDENTIAL_MAX_AGE: t.Final = 3600

SpaceTokenKind = te.Literal['delegation', 'credential', 'client_attestation']

_SPACE_HOST_SERVICE: t.Final = 'atproto_pds'
_SIGNING_KEY_ID: t.Final = '#atproto'
_CLIENT_ATTESTATION_LIFETIME: t.Final = 60
_JTI_SIZE: t.Final = 16

_BASE64URL_REGEX: t.Final = re.compile(r'[A-Za-z0-9_-]+')


@dataclass(frozen=True)
class _TokenSpec:
    typ: str
    kid: t.Optional[str]
    requires_aud: bool
    requires_cnf: bool


# a credential has no audience: the signature of each request binds its use to one
_TOKEN_SPECS: t.Final[t.Dict[SpaceTokenKind, _TokenSpec]] = {
    'delegation': _TokenSpec(DELEGATION_TOKEN_TYP, _SIGNING_KEY_ID, requires_aud=True, requires_cnf=False),
    'credential': _TokenSpec(SPACE_CREDENTIAL_TYP, _SIGNING_KEY_ID, requires_aud=False, requires_cnf=True),
    'client_attestation': _TokenSpec(CLIENT_ATTESTATION_TYP, None, requires_aud=True, requires_cnf=False),
}


@dataclass(frozen=True)
class SpaceToken:
    """Claims of a delegation token, a space credential or a client attestation.

    Attributes:
        iss: Issuer: the account, the space authority or the client ID.
        sub: URI of the space, or the client ID in a client attestation.
        exp: Expiration as a Unix timestamp.
        jti: Unique ID of the token.
        iat: Time of issue as a Unix timestamp. A space credential always has it.
        aud: Audience. A space credential has none.
        key_id: DID key that a space credential is bound to.
    """

    iss: str
    sub: str
    exp: float
    jti: str
    iat: t.Optional[float] = None
    aud: t.Optional[str] = None
    key_id: t.Optional[str] = None


def get_space_host_audience(space_did: str) -> str:
    """Get the audience that names the host of a space in delegation tokens and client attestations.

    Args:
        space_did: DID of the space authority.

    Returns:
        :obj:`str`: Audience.
    """
    return f'{space_did}#{_SPACE_HOST_SERVICE}'


def _decode_segment(segment: str, name: str) -> t.Dict[str, t.Any]:
    # the decoder skips the characters that are not base64url
    if not _BASE64URL_REGEX.fullmatch(segment):
        raise SpaceTokenError(f'Could not parse token {name}')

    try:
        decoded = json.loads(base64url_decode(segment))
    except (ValueError, RecursionError) as e:
        raise SpaceTokenError(f'Could not parse token {name}') from e

    if not isinstance(decoded, dict):
        raise SpaceTokenError(f'Could not parse token {name}')

    return decoded


def _get_string(data: t.Mapping[str, t.Any], name: str) -> t.Optional[str]:
    value = data.get(name)
    return value if isinstance(value, str) and value else None


def _get_number(data: t.Mapping[str, t.Any], name: str) -> t.Optional[float]:
    value = data.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def _get_key_id(payload: t.Mapping[str, t.Any]) -> t.Optional[str]:
    cnf = payload.get('cnf')
    key_id = _get_string(cnf, 'kid') if isinstance(cnf, dict) else None
    if key_id is None or not is_did(key_id):
        return None

    return key_id


def _require_string(payload: t.Mapping[str, t.Any], name: str, code: str = 'BadJwt') -> str:
    value = _get_string(payload, name)
    if value is None:
        raise SpaceTokenError(f'Missing token "{name}"', code)

    return value


def _check_header(header: t.Mapping[str, t.Any], spec: _TokenSpec) -> None:
    if header.get('typ') != spec.typ:
        raise SpaceTokenError(f'Wrong token type: expected "{spec.typ}", got "{header.get("typ")}"', 'BadJwtType')

    if _get_string(header, 'alg') is None:
        raise SpaceTokenError('Missing token "alg"')

    if spec.kid and header.get('kid') != spec.kid:
        raise SpaceTokenError(f'Wrong token "kid": expected "{spec.kid}", got "{header.get("kid")}"')


def parse_space_token(kind: SpaceTokenKind, token: str) -> SpaceToken:
    """Parse a space token and check its structure.

    Note:
        The signature and the expiration are not verified.

    Args:
        kind: ``'delegation'``, ``'credential'`` or ``'client_attestation'``.
        token: JWT in the compact serialization.

    Returns:
        :obj:`SpaceToken`: Claims of the token.

    Raises:
        :class:`atproto_space.exceptions.SpaceTokenError`: The token is not a well-formed token of this kind.
    """
    spec = _TOKEN_SPECS[kind]

    segments = token.split('.')
    if len(segments) != 3:
        raise SpaceTokenError('Malformed token: expected 3 parts')

    header = _decode_segment(segments[0], 'header')
    payload = _decode_segment(segments[1], 'payload')
    if not _BASE64URL_REGEX.fullmatch(segments[2]):
        raise SpaceTokenError('Could not parse token signature')

    _check_header(header, spec)

    iss = _require_string(payload, 'iss', 'BadJwtIss')
    sub = _require_string(payload, 'sub', 'BadJwtSub')

    exp = _get_number(payload, 'exp')
    if exp is None:
        raise SpaceTokenError('Missing token "exp"')

    aud = _get_string(payload, 'aud')
    if spec.requires_aud and aud is None:
        raise SpaceTokenError('Missing token "aud"', 'BadJwtAudience')

    key_id = _get_key_id(payload)
    if spec.requires_cnf and key_id is None:
        raise SpaceTokenError('Missing token "cnf.kid"', 'BadJwtCnf')

    jti = _require_string(payload, 'jti')

    iat = _get_number(payload, 'iat')
    if kind == 'credential' and (iat is None or exp <= iat or exp - iat > SPACE_CREDENTIAL_MAX_AGE):
        raise SpaceTokenError('Invalid space credential lifetime')

    if kind == 'client_attestation' and iss != sub:
        raise SpaceTokenError('Client attestation "iss" and "sub" must both be the client ID', 'BadJwtIss')

    return SpaceToken(iss=iss, sub=sub, exp=exp, jti=jti, iat=iat, aud=aud, key_id=key_id)


def create_client_attestation(
    client_id: str,
    audience: str,
    private_key: ec.EllipticCurvePrivateKey,
    kid: t.Optional[str] = None,
    expires_in: int = _CLIENT_ATTESTATION_LIFETIME,
) -> str:
    """Create a proof of the identity of an OAuth client for the host of a space.

    Args:
        client_id: Client ID of the OAuth client.
        audience: Audience that names the host of the space. See :func:`get_space_host_audience`.
        private_key: P-256 private key from the JWKS of the client.
        kid: ID of the key in the JWKS of the client.
        expires_in: Lifetime of the attestation in seconds.

    Returns:
        :obj:`str`: Client attestation, a JWT in the compact serialization.

    Raises:
        :class:`atproto_crypto.exceptions.UnsupportedKeyTypeError`: The private key is not a P-256 key.
    """
    if not isinstance(private_key.curve, ec.SECP256R1):
        raise UnsupportedKeyTypeError('Client attestation key must be a P-256 key')

    header = {'alg': P256_JWT_ALG, 'typ': CLIENT_ATTESTATION_TYP}
    if kid:
        header['kid'] = kid

    issued_at = int(time.time())
    payload = {
        'iss': client_id,
        'sub': client_id,
        'aud': audience,
        'iat': issued_at,
        'exp': issued_at + expires_in,
        'jti': secrets.token_hex(_JTI_SIZE),
    }

    return sign_jwt(header, payload, private_key)
