"""Tests for PKCE implementation."""

import hashlib
from base64 import urlsafe_b64encode

import pytest
from atproto_oauth.pkce import PKCEManager


def test_generate_verifier_default_length() -> None:
    """Test generating PKCE verifier with default length."""
    verifier = PKCEManager.generate_verifier()
    assert isinstance(verifier, str)
    assert 43 <= len(verifier) <= 128


def test_generate_verifier_custom_length() -> None:
    """Test generating PKCE verifier with custom length."""
    length = 64
    verifier = PKCEManager.generate_verifier(length)
    assert len(verifier) == length


def test_generate_verifier_invalid_length() -> None:
    """Test that invalid length raises error."""
    with pytest.raises(ValueError, match='must be between 43 and 128'):
        PKCEManager.generate_verifier(20)

    with pytest.raises(ValueError, match='must be between 43 and 128'):
        PKCEManager.generate_verifier(200)


def test_generate_challenge() -> None:
    """Test generating S256 challenge from verifier."""
    verifier = 'test_verifier_123456789'
    challenge = PKCEManager.generate_challenge(verifier)

    # Verify it's base64url encoded SHA256
    expected_digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    expected_challenge = urlsafe_b64encode(expected_digest).decode('utf-8').rstrip('=')

    assert challenge == expected_challenge


def test_generate_pair() -> None:
    """Test generating verifier and challenge pair."""
    verifier, challenge = PKCEManager.generate_pair()

    # Verify verifier format
    assert isinstance(verifier, str)
    assert 43 <= len(verifier) <= 128

    # Verify challenge matches verifier
    expected_challenge = PKCEManager.generate_challenge(verifier)
    assert challenge == expected_challenge


def test_challenge_is_deterministic() -> None:
    """Test that same verifier always produces same challenge."""
    verifier = PKCEManager.generate_verifier()
    challenge1 = PKCEManager.generate_challenge(verifier)
    challenge2 = PKCEManager.generate_challenge(verifier)

    assert challenge1 == challenge2
