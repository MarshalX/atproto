import typing as t
from dataclasses import dataclass, field

from atproto_crypto.exceptions import InvalidJwkError
from atproto_crypto.jwk import Jwk, get_public_jwk, load_private_jwk

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

CLIENT_ASSERTION_ALG: t.Final = 'ES256'

_PUBLIC_JWK_MEMBERS: t.Final = ('kty', 'crv', 'x', 'y', 'kid')


@dataclass(frozen=True)
class SigningKey:
    kid: str
    private_key: 'EllipticCurvePrivateKey' = field(repr=False)
    public_jwk: Jwk


class Keyset:
    """Client authentication keys of a confidential client.

    Args:
        keys: Private P-256 JWKs, each with a unique ``kid``. The first one signs new sessions.
    """

    def __init__(self, keys: t.Optional[t.Iterable[t.Mapping[str, t.Any]]] = None) -> None:
        self._keys: t.Dict[str, SigningKey] = {}

        for jwk in keys or ():
            kid = jwk.get('kid')
            if not isinstance(kid, str) or not kid:
                raise ValueError('Every client authentication key must have a "kid"')

            if kid in self._keys:
                raise ValueError(f'Duplicate client authentication key "{kid}"')

            try:
                private_key = load_private_jwk(jwk)
                public_jwk = get_public_jwk(jwk)
            except InvalidJwkError as e:
                raise ValueError(f'Client authentication key "{kid}" is not a private P-256 JWK') from e

            self._keys[kid] = SigningKey(
                kid=kid,
                private_key=private_key,
                public_jwk={
                    **{name: public_jwk[name] for name in _PUBLIC_JWK_MEMBERS},
                    'use': 'sig',
                    'alg': CLIENT_ASSERTION_ALG,
                },
            )

    def __len__(self) -> int:
        return len(self._keys)

    def get(self, kid: t.Optional[str]) -> t.Optional[SigningKey]:
        return self._keys.get(kid) if kid else None

    @property
    def default(self) -> t.Optional[SigningKey]:
        """Key that signs new sessions."""
        return next(iter(self._keys.values()), None)

    @property
    def public_jwks(self) -> t.Dict[str, t.List[Jwk]]:
        """JWK Set with the public halves of the keys."""
        return {'keys': [dict(key.public_jwk) for key in self._keys.values()]}
