"""Builds the tokens that a PDS and a space host issue. The SDK only parses them."""

import json
import secrets
import time
import typing as t

from atproto_crypto.jwk import base64url_encode
from atproto_space.tokens import DELEGATION_TOKEN_TYP, SPACE_CREDENTIAL_TYP

_ALG = 'ES256K'
_KID = '#atproto'


def _encode_segment(segment: t.Mapping[str, t.Any]) -> str:
    return base64url_encode(json.dumps(segment, separators=(',', ':')).encode('UTF-8'))


def build_token(header: t.Mapping[str, t.Any], payload: t.Mapping[str, t.Any]) -> str:
    """Build a JWT with a signature that is not valid: the SDK never verifies it."""
    return f'{_encode_segment(header)}.{_encode_segment(payload)}.{base64url_encode(b"signature")}'


def _build_claims(expires_in: int, issued_at: t.Optional[int]) -> t.Dict[str, t.Any]:
    if issued_at is None:
        issued_at = int(time.time())

    return {'iat': issued_at, 'exp': issued_at + expires_in, 'jti': secrets.token_hex(16)}


def build_delegation_token(
    iss: str, sub: str, aud: str, expires_in: int = 60, issued_at: t.Optional[int] = None
) -> str:
    return build_token(
        {'alg': _ALG, 'typ': DELEGATION_TOKEN_TYP, 'kid': _KID},
        {'iss': iss, 'sub': sub, 'aud': aud, **_build_claims(expires_in, issued_at)},
    )


def build_space_credential(
    iss: str, sub: str, key_id: str, expires_in: int = 600, issued_at: t.Optional[int] = None
) -> str:
    return build_token(
        {'alg': _ALG, 'typ': SPACE_CREDENTIAL_TYP, 'kid': _KID},
        {'iss': iss, 'sub': sub, 'cnf': {'kid': key_id}, **_build_claims(expires_in, issued_at)},
    )
