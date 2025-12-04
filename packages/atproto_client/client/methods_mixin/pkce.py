"""PKCE (Proof Key for Code Exchange) implementation."""

import base64
import hashlib
import secrets
import typing as t


class PKCEManager:
    """Manages PKCE code verifier and challenge generation."""

    @staticmethod
    def generate_verifier(length: int = 128) -> str:
        """Generate a PKCE code verifier.

        Args:
        length: Length of the verifier (43-128 characters).

        Returns:
        Base64url-encoded verifier string.

        Raises:
        ValueError: If length is not between 43 and 128.
        """
        if not 43 <= length <= 128:
            raise ValueError('PKCE verifier length must be between 43 and 128')

        # Generate random bytes and encode as base64url
        verifier_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(verifier_bytes).decode('utf-8').rstrip('=')[:length]

    @staticmethod
    def generate_challenge(verifier: str) -> str:
        """Generate S256 PKCE code challenge from verifier.

        Args:
        verifier: The code verifier string.

        Returns:
        Base64url-encoded SHA256 hash of the verifier.
        """
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

    @classmethod
    def generate_pair(cls, length: int = 128) -> t.Tuple[str, str]:
        """Generate both verifier and challenge.

        Args:
        length: Length of the verifier.

        Returns:
        Tuple of (verifier, challenge).
        """
        verifier = cls.generate_verifier(length)
        challenge = cls.generate_challenge(verifier)
        return verifier, challenge
