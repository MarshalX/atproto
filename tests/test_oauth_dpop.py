"""Tests for DPoP implementation."""

import json

import httpx
from atproto_oauth.dpop import DPoPManager


def test_generate_keypair() -> None:
    """Test generating DPoP keypair."""
    key = DPoPManager.generate_keypair()
    assert key is not None

    # Verify it's an EC key
    from cryptography.hazmat.primitives.asymmetric import ec

    assert isinstance(key, ec.EllipticCurvePrivateKey)


def test_create_proof() -> None:
    """Test creating DPoP proof JWT."""
    key = DPoPManager.generate_keypair()

    proof = DPoPManager.create_proof(
        method='GET',
        url='https://example.com/api',
        private_key=key,
    )

    # Verify JWT structure
    assert isinstance(proof, str)
    parts = proof.split('.')
    assert len(parts) == 3  # header.payload.signature

    # Decode and verify header
    import base64

    header_json = base64.urlsafe_b64decode(parts[0] + '==')
    header = json.loads(header_json)

    assert header['typ'] == 'dpop+jwt'
    assert header['alg'] == 'ES256'
    assert 'jwk' in header

    # Decode and verify payload
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert payload['htm'] == 'GET'
    assert payload['htu'] == 'https://example.com/api'
    assert 'jti' in payload
    assert 'iat' in payload
    assert 'exp' in payload


def test_create_proof_with_nonce() -> None:
    """Test creating DPoP proof with nonce."""
    key = DPoPManager.generate_keypair()
    nonce = 'test-nonce-123'

    proof = DPoPManager.create_proof(
        method='POST',
        url='https://example.com/api',
        private_key=key,
        nonce=nonce,
    )

    # Decode payload and verify nonce
    import base64

    parts = proof.split('.')
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert payload['nonce'] == nonce


def test_create_proof_with_access_token() -> None:
    """Test creating DPoP proof with access token hash."""
    key = DPoPManager.generate_keypair()
    access_token = 'test-access-token'

    proof = DPoPManager.create_proof(
        method='POST',
        url='https://example.com/api',
        private_key=key,
        access_token=access_token,
    )

    # Decode payload and verify ath claim
    import base64
    import hashlib

    parts = proof.split('.')
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert 'ath' in payload

    # Verify ath is correct hash
    expected_hash = hashlib.sha256(access_token.encode('utf-8')).digest()
    expected_ath = base64.urlsafe_b64encode(expected_hash).decode('utf-8').rstrip('=')
    assert payload['ath'] == expected_ath


def test_is_dpop_nonce_error() -> None:
    """Test detecting DPoP nonce error responses."""
    # Test with error in JSON body
    response = httpx.Response(
        status_code=401,
        json={'error': 'use_dpop_nonce'},
        headers={'DPoP-Nonce': 'new-nonce'},
    )
    assert DPoPManager.is_dpop_nonce_error(response)

    # Test with error in WWW-Authenticate header
    response = httpx.Response(
        status_code=401,
        headers={
            'WWW-Authenticate': 'DPoP error="use_dpop_nonce"',
            'DPoP-Nonce': 'new-nonce',
        },
    )
    assert DPoPManager.is_dpop_nonce_error(response)

    # Test normal response
    response = httpx.Response(status_code=200, json={'success': True})
    assert not DPoPManager.is_dpop_nonce_error(response)


def test_extract_nonce_from_response() -> None:
    """Test extracting DPoP nonce from response."""
    response = httpx.Response(
        status_code=401,
        headers={'DPoP-Nonce': 'test-nonce-456'},
    )

    nonce = DPoPManager.extract_nonce_from_response(response)
    assert nonce == 'test-nonce-456'

    # Test response without nonce
    response = httpx.Response(status_code=200)
    nonce = DPoPManager.extract_nonce_from_response(response)
    assert nonce is None


def test_dpop_signature_format() -> None:
    """Test that DPoP signature uses IEEE P1363 format (64 bytes for ES256)."""
    key = DPoPManager.generate_keypair()

    proof = DPoPManager.create_proof(
        method='POST',
        url='https://example.com/token',
        private_key=key,
    )

    # Decode signature
    import base64

    parts = proof.split('.')
    # Add padding if needed
    signature_b64 = parts[2] + '=' * (4 - len(parts[2]) % 4)
    signature_bytes = base64.urlsafe_b64decode(signature_b64)

    # ES256 signature should be 64 bytes (32 for r, 32 for s)
    assert len(signature_bytes) == 64, f'Signature length is {len(signature_bytes)}, expected 64'


def test_dpop_htu_strips_query_and_fragment() -> None:
    """Test that htu field strips query and fragment per RFC 9449."""
    key = DPoPManager.generate_keypair()

    # Test with query parameters
    proof = DPoPManager.create_proof(
        method='POST',
        url='https://example.com/token?param=value&other=test',
        private_key=key,
    )

    import base64

    parts = proof.split('.')
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert payload['htu'] == 'https://example.com/token'

    # Test with fragment
    proof = DPoPManager.create_proof(
        method='GET',
        url='https://example.com/api#section',
        private_key=key,
    )

    parts = proof.split('.')
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert payload['htu'] == 'https://example.com/api'

    # Test with both query and fragment
    proof = DPoPManager.create_proof(
        method='GET',
        url='https://example.com/api?foo=bar#section',
        private_key=key,
    )

    parts = proof.split('.')
    payload_json = base64.urlsafe_b64decode(parts[1] + '==')
    payload = json.loads(payload_json)

    assert payload['htu'] == 'https://example.com/api'


def test_dpop_jwk_format() -> None:
    """Test that JWK in header is properly formatted."""
    key = DPoPManager.generate_keypair()

    proof = DPoPManager.create_proof(
        method='POST',
        url='https://example.com/token',
        private_key=key,
    )

    import base64

    parts = proof.split('.')
    header_json = base64.urlsafe_b64decode(parts[0] + '==')
    header = json.loads(header_json)

    jwk = header['jwk']

    # Verify JWK structure
    assert jwk['kty'] == 'EC'
    assert jwk['crv'] == 'P-256'
    assert 'x' in jwk
    assert 'y' in jwk
    # Must NOT contain private key
    assert 'd' not in jwk
