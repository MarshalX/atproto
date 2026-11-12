import hashlib
import secrets
import typing as t

from atproto_crypto.jwk import base64url_encode

PKCE_METHOD: t.Final = 'S256'


def get_pkce_challenge(verifier: str) -> str:
    """Compute the S256 challenge of a PKCE verifier."""
    return base64url_encode(hashlib.sha256(verifier.encode('ascii')).digest())


def generate_pkce(size: int = 32) -> t.Tuple[str, str]:
    """Generate a PKCE verifier and its S256 challenge.

    Args:
        size: Random bytes in the verifier, 32 to 96.

    Returns:
        :obj:`tuple` of :obj:`str`: Verifier and challenge.
    """
    if not 32 <= size <= 96:
        raise ValueError('PKCE verifier must be made of 32 to 96 random bytes')

    verifier = base64url_encode(secrets.token_bytes(size))
    return verifier, get_pkce_challenge(verifier)
