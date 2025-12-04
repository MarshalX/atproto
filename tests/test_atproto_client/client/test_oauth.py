"""Tests for OAuth mixin and related components."""

import json
import typing as t
from base64 import urlsafe_b64decode
from unittest.mock import MagicMock

import pytest
from atproto_client.client.client import Client
from atproto_client.client.methods_mixin.dpop import DPoPManager
from atproto_client.client.methods_mixin.pkce import PKCEManager


class TestPKCEManager:
    """Tests for PKCEManager."""

    def test_generate_pair_produces_valid_challenge(self) -> None:
        """PKCE pair should produce matching verifier and challenge."""
        verifier, challenge = PKCEManager.generate_pair()

        assert len(verifier) == 128
        assert PKCEManager.generate_challenge(verifier) == challenge


class TestDPoPManager:
    """Tests for DPoPManager."""

    def test_generate_keypair(self) -> None:
        """Should generate ES256 keypair on P-256 curve."""
        from cryptography.hazmat.primitives.asymmetric import ec

        key = DPoPManager.generate_keypair()
        assert isinstance(key, ec.EllipticCurvePrivateKey)
        assert isinstance(key.curve, ec.SECP256R1)

    def test_create_proof_returns_valid_jwt(self) -> None:
        """Proof should be valid JWT with required DPoP claims."""
        key = DPoPManager.generate_keypair()
        proof = DPoPManager.create_proof(
            method='POST',
            url='https://example.com/token?query=ignored',
            private_key=key,
            nonce='test-nonce',
        )

        # Decode and verify structure
        parts = proof.split('.')
        assert len(parts) == 3

        header = json.loads(urlsafe_b64decode(parts[0] + '=='))
        payload = json.loads(urlsafe_b64decode(parts[1] + '=='))

        assert header['typ'] == 'dpop+jwt'
        assert header['alg'] == 'ES256'
        assert 'jwk' in header

        assert payload['htm'] == 'POST'
        assert payload['htu'] == 'https://example.com/token'  # query stripped
        assert payload['nonce'] == 'test-nonce'

    @pytest.mark.parametrize(
        'status_code,headers,json_body,expected',
        [
            # WWW-Authenticate header detection
            (401, {'WWW-Authenticate': 'DPoP error="use_dpop_nonce"'}, None, True),
            # JSON body detection
            (400, {}, {'error': 'use_dpop_nonce'}, True),
            # Not a nonce error - different error
            (401, {'WWW-Authenticate': 'Bearer error="invalid_token"'}, None, False),
            # Not a nonce error - success response
            (200, {}, None, False),
        ],
    )
    def test_is_dpop_nonce_error(
        self, status_code: int, headers: dict, json_body: t.Optional[dict], expected: bool
    ) -> None:
        """Should detect DPoP nonce errors from various response formats."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.headers = headers
        mock_response.json.return_value = json_body

        assert DPoPManager.is_dpop_nonce_error(mock_response) is expected

    @pytest.mark.parametrize(
        'headers,expected_nonce',
        [
            ({'DPoP-Nonce': 'server-nonce-123'}, 'server-nonce-123'),
            ({'dpop-nonce': 'lowercase-nonce'}, 'lowercase-nonce'),
            ({}, None),
        ],
    )
    def test_extract_nonce_from_response(self, headers: dict, expected_nonce: t.Optional[str]) -> None:
        """Should extract DPoP nonce from response headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = headers

        assert DPoPManager.extract_nonce_from_response(mock_response) == expected_nonce


class TestOAuthMixin:
    """Tests for OauthSessionMethodsMixin integration with Client."""

    def test_client_works_without_oauth_params(self) -> None:
        """Client should instantiate normally without OAuth configuration."""
        client = Client()
        assert client._oauth_client_id is None
        assert client._oauth_initialized is False

    def test_client_accepts_oauth_params(self) -> None:
        """Client should accept and store OAuth configuration."""
        client = Client(
            client_id='https://example.com/client',
            redirect_uri='https://example.com/callback',
            scope='atproto',
        )
        assert client._oauth_client_id == 'https://example.com/client'

    def test_ensure_oauth_initialized_requires_config(self) -> None:
        """_ensure_oauth_initialized should raise without OAuth config."""
        client = Client()
        with pytest.raises(ValueError, match='OAuth not configured'):
            client._ensure_oauth_initialized()
