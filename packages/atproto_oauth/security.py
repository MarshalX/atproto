"""Security utilities for OAuth implementation."""

import typing as t
from urllib.parse import urlparse

import httpx

# Hardened HTTP client configuration
DEFAULT_TIMEOUT = 5.0
MAX_REDIRECTS = 3
ALLOWED_SCHEMES = {'https', 'http'}  # http only for localhost
BLOCKED_HOSTS = {
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    '::1',
    '169.254.169.254',  # AWS metadata
    'metadata.google.internal',  # GCP metadata
}


def is_safe_url(url: str, allow_localhost: bool = False) -> bool:
    """Validate URL for security (SSRF protection).

    Args:
        url: URL to validate.
        allow_localhost: Whether to allow localhost URLs.

    Returns:
        True if URL is safe to use.
    """
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        # For http, only allow if allow_localhost and is actually localhost
        if parsed.scheme == 'http':
            if not allow_localhost:
                return False
            if parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
                return False

        # Check for blocked hosts
        if parsed.hostname in BLOCKED_HOSTS and not allow_localhost:
            return False

        # Check for IP addresses in private ranges (basic check)
        if parsed.hostname:
            # Block obvious private IPs
            if parsed.hostname.startswith('10.'):
                return False
            if parsed.hostname.startswith('172.') and 16 <= int(parsed.hostname.split('.')[1]) <= 31:
                return False
            if parsed.hostname.startswith('192.168.'):
                return False

        return True
    except Exception:
        return False


def get_hardened_client(
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = MAX_REDIRECTS,
) -> httpx.Client:
    """Create hardened HTTP client with security settings.

    Args:
        timeout: Request timeout in seconds.
        max_redirects: Maximum number of redirects to follow.

    Returns:
        Configured httpx.Client.
    """
    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        max_redirects=max_redirects,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    )


def get_hardened_async_client(
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = MAX_REDIRECTS,
) -> httpx.AsyncClient:
    """Create hardened async HTTP client with security settings.

    Args:
        timeout: Request timeout in seconds.
        max_redirects: Maximum number of redirects to follow.

    Returns:
        Configured httpx.AsyncClient.
    """
    return httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        max_redirects=max_redirects,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    )


def validate_authserver_metadata(metadata: t.Dict[str, t.Any], fetch_url: str) -> None:
    """Validate authorization server metadata against ATProto requirements.

    Args:
        metadata: Metadata dictionary from server.
        fetch_url: URL where metadata was fetched from.

    Raises:
        ValueError: If metadata doesn't meet requirements.
    """
    issuer_url = urlparse(metadata['issuer'])
    fetch_parsed = urlparse(fetch_url)

    # Issuer must match fetch URL host
    if issuer_url.hostname != fetch_parsed.hostname:
        raise ValueError(f'Issuer hostname mismatch: {issuer_url.hostname} != {fetch_parsed.hostname}')

    # Issuer must be HTTPS with no path/params/fragment
    if issuer_url.scheme != 'https':
        raise ValueError(f'Issuer must be HTTPS: {issuer_url.scheme}')
    if issuer_url.port is not None:
        raise ValueError(f'Issuer must not have explicit port: {issuer_url.port}')
    if issuer_url.path not in ('', '/'):
        raise ValueError(f'Issuer must not have path: {issuer_url.path}')
    if issuer_url.params or issuer_url.fragment:
        raise ValueError('Issuer must not have params or fragment')

    # Check required grant types and methods
    required_checks = [
        ('code' in metadata.get('response_types_supported', []), 'response_types_supported must include "code"'),
        (
            'authorization_code' in metadata.get('grant_types_supported', []),
            'grant_types_supported must include "authorization_code"',
        ),
        (
            'refresh_token' in metadata.get('grant_types_supported', []),
            'grant_types_supported must include "refresh_token"',
        ),
        (
            'S256' in metadata.get('code_challenge_methods_supported', []),
            'code_challenge_methods_supported must include "S256"',
        ),
        (
            'none' in metadata.get('token_endpoint_auth_methods_supported', []),
            'token_endpoint_auth_methods_supported must include "none"',
        ),
        (
            'private_key_jwt' in metadata.get('token_endpoint_auth_methods_supported', []),
            'token_endpoint_auth_methods_supported must include "private_key_jwt"',
        ),
        (
            'ES256' in metadata.get('token_endpoint_auth_signing_alg_values_supported', []),
            'token_endpoint_auth_signing_alg_values_supported must include "ES256"',
        ),
        ('atproto' in metadata.get('scopes_supported', []), 'scopes_supported must include "atproto"'),
        (
            metadata.get('authorization_response_iss_parameter_supported') is True,
            'authorization_response_iss_parameter_supported must be true',
        ),
        (
            metadata.get('pushed_authorization_request_endpoint') is not None,
            'pushed_authorization_request_endpoint is required',
        ),
        (
            metadata.get('require_pushed_authorization_requests') is True,
            'require_pushed_authorization_requests must be true',
        ),
        (
            'ES256' in metadata.get('dpop_signing_alg_values_supported', []),
            'dpop_signing_alg_values_supported must include "ES256"',
        ),
        (
            metadata.get('client_id_metadata_document_supported') is True,
            'client_id_metadata_document_supported must be true',
        ),
    ]

    for check, error_msg in required_checks:
        if not check:
            raise ValueError(error_msg)
