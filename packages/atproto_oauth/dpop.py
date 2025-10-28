"""DPoP (Demonstrating Proof-of-Possession) implementation."""

import hashlib
import json
import secrets
import time
import typing as t
from base64 import urlsafe_b64encode

import httpx
from cryptography.hazmat.primitives.asymmetric import ec

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


class DPoPManager:
    """Manages DPoP proof generation for OAuth."""

    @staticmethod
    def generate_keypair() -> 'EllipticCurvePrivateKey':
        """Generate ES256 keypair for DPoP.

        Returns:
            EC private key (P-256 curve).
        """
        return ec.generate_private_key(ec.SECP256R1())

    @staticmethod
    def _key_to_jwk(private_key: 'EllipticCurvePrivateKey', include_private: bool = False) -> t.Dict[str, t.Any]:
        """Convert EC private key to JWK format.

        Args:
            private_key: The EC private key.
            include_private: Whether to include private key components.

        Returns:
            JWK dictionary.
        """
        public_key = private_key.public_key()
        public_numbers = public_key.public_numbers()

        # Convert to bytes and base64url encode
        def int_to_base64url(n: int, length: int) -> str:
            byte_len = (length + 7) // 8
            return urlsafe_b64encode(n.to_bytes(byte_len, 'big')).decode('utf-8').rstrip('=')

        jwk = {
            'kty': 'EC',
            'crv': 'P-256',
            'x': int_to_base64url(public_numbers.x, 256),
            'y': int_to_base64url(public_numbers.y, 256),
        }

        if include_private:
            private_numbers = private_key.private_numbers()
            jwk['d'] = int_to_base64url(private_numbers.private_value, 256)

        return jwk

    @staticmethod
    def _sign_jwt(
        header: t.Dict[str, t.Any], payload: t.Dict[str, t.Any], private_key: 'EllipticCurvePrivateKey'
    ) -> str:
        """Sign a JWT using ES256.

        Args:
            header: JWT header.
            payload: JWT payload.
            private_key: EC private key for signing.

        Returns:
            Complete JWT string.
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec

        # Encode header and payload
        header_b64 = urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode()).decode().rstrip('=')
        payload_b64 = urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode().rstrip('=')

        # Create signing input
        signing_input = f'{header_b64}.{payload_b64}'.encode()

        # Sign
        signature = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))

        # Encode signature
        signature_b64 = urlsafe_b64encode(signature).decode().rstrip('=')

        return f'{header_b64}.{payload_b64}.{signature_b64}'

    @classmethod
    def create_proof(
        cls,
        method: str,
        url: str,
        private_key: 'EllipticCurvePrivateKey',
        nonce: t.Optional[str] = None,
        access_token: t.Optional[str] = None,
    ) -> str:
        """Generate DPoP proof JWT.

        Args:
            method: HTTP method (e.g., 'GET', 'POST').
            url: Full URL of the request.
            private_key: EC private key for signing.
            nonce: Optional server-provided nonce.
            access_token: Optional access token (for 'ath' claim).

        Returns:
            DPoP proof JWT string.
        """
        # Get public key JWK
        public_jwk = cls._key_to_jwk(private_key, include_private=False)

        # Create header
        header = {
            'typ': 'dpop+jwt',
            'alg': 'ES256',
            'jwk': public_jwk,
        }

        # Create payload
        now = int(time.time())
        payload = {
            'jti': secrets.token_urlsafe(16),
            'htm': method.upper(),
            'htu': url,
            'iat': now,
            'exp': now + 60,  # Valid for 60 seconds
        }

        # Add optional claims
        if nonce:
            payload['nonce'] = nonce

        if access_token:
            # Hash access token for 'ath' claim (same as PKCE S256)
            ath_hash = hashlib.sha256(access_token.encode('utf-8')).digest()
            payload['ath'] = urlsafe_b64encode(ath_hash).decode('utf-8').rstrip('=')

        return cls._sign_jwt(header, payload, private_key)

    @staticmethod
    def extract_nonce_from_response(response: httpx.Response) -> t.Optional[str]:
        """Extract DPoP nonce from HTTP response.

        Checks both the 'DPoP-Nonce' header and error responses.

        Args:
            response: HTTP response object.

        Returns:
            DPoP nonce string if present, None otherwise.
        """
        # Check DPoP-Nonce header
        if nonce := response.headers.get('DPoP-Nonce'):
            return nonce

        # Check for error response with use_dpop_nonce
        if response.status_code in (400, 401):
            try:
                error_body = response.json()
                if isinstance(error_body, dict) and error_body.get('error') == 'use_dpop_nonce':
                    return response.headers.get('DPoP-Nonce')
            except Exception:
                pass

        return None

    @staticmethod
    def is_dpop_nonce_error(response: httpx.Response) -> bool:
        """Check if response indicates DPoP nonce error.

        Args:
            response: HTTP response object.

        Returns:
            True if response indicates need for new DPoP nonce.
        """
        if response.status_code not in (400, 401):
            return False

        # Check WWW-Authenticate header
        if www_auth := response.headers.get('WWW-Authenticate', ''):
            if 'use_dpop_nonce' in www_auth.lower():
                return True

        # Check JSON error response
        try:
            error_body = response.json()
            if isinstance(error_body, dict) and error_body.get('error') == 'use_dpop_nonce':
                return True
        except Exception:
            pass

        return False
