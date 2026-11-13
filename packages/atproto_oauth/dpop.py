import hashlib
import re
import secrets
import time
import typing as t
from urllib.parse import urlsplit, urlunsplit

from atproto_crypto.jwk import Jwk, base64url_encode, get_public_jwk, load_private_jwk
from atproto_crypto.jws import sign_jwt

from atproto_oauth.stores import MemoryStore

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

DPOP_ALG: t.Final = 'ES256'

_NONCE_TTL: t.Final = 60.0
_NONCE_MAX_SIZE: t.Final = 100

_USE_DPOP_NONCE: t.Final = 'use_dpop_nonce'
_INVALID_TOKEN: t.Final = 'invalid_token'  # noqa: S105
_WWW_AUTHENTICATE_ERROR: t.Final = re.compile(r'\berror="([^"]*)"')


class DpopKey:
    """Private key of a session, loaded once.

    Args:
        jwk: Private P-256 JWK.
    """

    def __init__(self, jwk: Jwk) -> None:
        self.jwk = jwk
        self.public_jwk: Jwk = {name: value for name, value in get_public_jwk(jwk).items() if name != 'kid'}
        self.private_key: EllipticCurvePrivateKey = load_private_jwk(jwk)


class NonceCache:
    """Latest DPoP nonce of each server, by origin."""

    def __init__(self) -> None:
        self._store: MemoryStore[str] = MemoryStore(ttl=_NONCE_TTL, max_size=_NONCE_MAX_SIZE)

    def get(self, origin: str) -> t.Optional[str]:
        return self._store.get(origin)

    def update(self, origin: str, nonce: t.Optional[str]) -> None:
        """Remember the nonce a server sent in its ``DPoP-Nonce`` header, if any."""
        if nonce and nonce != self._store.get(origin):
            self._store.set(origin, nonce)


def generate_nonce(size: int = 16) -> str:
    """Generate a random URL-safe token for ``state`` and ``jti`` values."""
    return base64url_encode(secrets.token_bytes(size))


def get_htu(url: str) -> str:
    """Return the URL without query and fragment, as required for the ``htu`` claim."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


def build_dpop_proof(
    key: DpopKey,
    method: str,
    url: str,
    nonce: t.Optional[str] = None,
    access_token: t.Optional[str] = None,
) -> str:
    """Build a DPoP proof JWT for a request.

    Args:
        key: Key of the session.
        method: HTTP method of the request.
        url: URL of the request.
        nonce: Latest nonce of the server.
        access_token: Access token sent with the request. Omit for requests to the authorization server.

    Returns:
        :obj:`str`: Value of the ``DPoP`` header.
    """
    payload: t.Dict[str, t.Any] = {
        'jti': generate_nonce(),
        'htm': method.upper(),
        'htu': get_htu(url),
        'iat': int(time.time()),
    }
    if nonce:
        payload['nonce'] = nonce

    if access_token:
        payload['ath'] = base64url_encode(hashlib.sha256(access_token.encode('ascii')).digest())

    return sign_jwt({'typ': 'dpop+jwt', 'alg': DPOP_ALG, 'jwk': key.public_jwk}, payload, key.private_key)


def _get_www_authenticate_error(www_authenticate: t.Optional[str], schemes: t.Tuple[str, ...]) -> t.Optional[str]:
    if not www_authenticate or not www_authenticate.startswith(schemes):
        return None

    match = _WWW_AUTHENTICATE_ERROR.search(www_authenticate)
    return match.group(1) if match else None


def is_auth_server_nonce_error(status_code: int, body: t.Any) -> bool:
    """Tell whether the authorization server asks to repeat the request with a new nonce."""
    return status_code == 400 and isinstance(body, dict) and body.get('error') == _USE_DPOP_NONCE


def is_resource_server_nonce_error(status_code: int, www_authenticate: t.Optional[str]) -> bool:
    """Tell whether the resource server asks to repeat the request with a new nonce."""
    return status_code == 401 and _get_www_authenticate_error(www_authenticate, ('DPoP ',)) == _USE_DPOP_NONCE


def is_invalid_token_error(status_code: int, www_authenticate: t.Optional[str]) -> bool:
    """Tell whether the resource server rejected the access token."""
    return status_code == 401 and _get_www_authenticate_error(www_authenticate, ('DPoP ', 'Bearer ')) == _INVALID_TOKEN
