import typing as t
from dataclasses import dataclass

import jwt as _jwt


@dataclass
class JwtPayload:
    exp: int  # expired at
    iat: int  # created at
    scope: str
    sub: str  # DID
    aud: t.Optional[str] = None  # DID
    jti: t.Optional[str] = None  # in refresh token only


def get_jwt_payload(token: str) -> JwtPayload:
    plain_payload = _jwt.decode(token, options={'verify_signature': False})
    return JwtPayload(**plain_payload)
