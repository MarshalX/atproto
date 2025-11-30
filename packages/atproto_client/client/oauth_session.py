from dataclasses import dataclass, field
from datetime import datetime, timezone
import typing as t
from urllib.parse import urlparse

from atproto_client.exceptions import UnsupportedAuthServerError, AuthServerMetadata

"""Authorization server metadata discovery."""

import httpx

import secrets

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
@dataclass
class TokenResponse:
    """Token response from authorization server."""

    access_token: str
    token_type: str
    scope: str
    sub: str  # DID
    refresh_token: t.Optional[str] = None
    expires_in: t.Optional[int] = None

def discover_authserver_from_pds(pds_url: str, timeout: float = 5.0) -> str:
    """Discover authorization server URL from PDS.

Args:
pds_url: PDS endpoint URL.
timeout: Request timeout in seconds.

Returns:
Authorization server URL.

Raises:
ValueError: If PDS URL is unsafe or response is invalid.
httpx.HTTPError: If request fails.
    """
    if not is_safe_url(pds_url):
        raise ValueError(f'Unsafe PDS URL: {pds_url}')

    with httpx.Client(timeout=timeout) as client:
        response = client.get(f'{pds_url}/.well-known/oauth-protected-resource')
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f'PDS returned non-200 status: {response.status_code}')

        data = response.json()
        if not isinstance(data, dict) or 'authorization_servers' not in data:
            raise ValueError('Invalid oauth-protected-resource response')

        auth_servers = data['authorization_servers']
        if not auth_servers or not isinstance(auth_servers, list):
            raise ValueError('No authorization servers found')

        return auth_servers[0]


def discover_authserver_from_pds(pds_url: str, timeout: float = 5.0) -> str:
    """Discover authorization server URL from PDS (synchronous).

        Args:
        pds_url: PDS endpoint URL.
        timeout: Request timeout in seconds.

        Returns:
        Authorization server URL.
    """
    if not is_safe_url(pds_url):
        raise ValueError(f'Unsafe PDS URL: {pds_url}')

    with httpx.Client(timeout=timeout) as client:
        response = client.get(f'{pds_url}/.well-known/oauth-protected-resource')
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f'PDS returned non-200 status: {response.status_code}')

        data = response.json()
        if not isinstance(data, dict) or 'authorization_servers' not in data:
            raise ValueError('Invalid oauth-protected-resource response')

        auth_servers = data['authorization_servers']
        if not auth_servers or not isinstance(auth_servers, list):
            raise ValueError('No authorization servers found')

        return auth_servers[0]


def fetch_authserver_metadata(authserver_url: str, timeout: float = 5.0) -> AuthServerMetadata:
    """Fetch and validate authorization server metadata.

        Args:
        authserver_url: Authorization server URL.
        timeout: Request timeout in seconds.

        Returns:
        Validated metadata object.

        Raises:
        ValueError: If URL is unsafe.
        UnsupportedAuthServerError: If metadata doesn't meet requirements.
        httpx.HTTPError: If request fails.
    """
    if not is_safe_url(authserver_url):
        raise ValueError(f'Unsafe authorization server URL: {authserver_url}')

    fetch_url = f'{authserver_url}/.well-known/oauth-authorization-server'

    with httpx.AsyncClient(timeout=timeout) as client:
        response = client.get(fetch_url)
        response.raise_for_status()

        metadata_dict = response.json()

        # Validate against ATProto requirements
        try:
            validate_authserver_metadata(metadata_dict, fetch_url)
        except ValueError as e:
            raise UnsupportedAuthServerError(str(e)) from e

        # Parse into model
        return AuthServerMetadata(
            issuer=metadata_dict['issuer'],
            authorization_endpoint=metadata_dict['authorization_endpoint'],
            token_endpoint=metadata_dict['token_endpoint'],
            pushed_authorization_request_endpoint=metadata_dict['pushed_authorization_request_endpoint'],
            response_types_supported=metadata_dict['response_types_supported'],
            grant_types_supported=metadata_dict['grant_types_supported'],
            code_challenge_methods_supported=metadata_dict['code_challenge_methods_supported'],
            token_endpoint_auth_methods_supported=metadata_dict['token_endpoint_auth_methods_supported'],
            token_endpoint_auth_signing_alg_values_supported=metadata_dict[
                'token_endpoint_auth_signing_alg_values_supported'
            ],
            scopes_supported=metadata_dict['scopes_supported'],
            dpop_signing_alg_values_supported=metadata_dict['dpop_signing_alg_values_supported'],
            authorization_response_iss_parameter_supported=metadata_dict[
                'authorization_response_iss_parameter_supported'
            ],
            require_pushed_authorization_requests=metadata_dict['require_pushed_authorization_requests'],
            client_id_metadata_document_supported=metadata_dict['client_id_metadata_document_supported'],
            revocation_endpoint=metadata_dict.get('revocation_endpoint'),
            jwks_uri=metadata_dict.get('jwks_uri'),
            require_request_uri_registration=metadata_dict.get('require_request_uri_registration'),
        )


def fetch_authserver_metadata(authserver_url: str, timeout: float = 5.0) -> AuthServerMetadata:
    """Fetch and validate authorization server metadata (synchronous).

        Args:
        authserver_url: Authorization server URL.
        timeout: Request timeout in seconds.

        Returns:
        Validated metadata object.
    """
    if not is_safe_url(authserver_url):
        raise ValueError(f'Unsafe authorization server URL: {authserver_url}')

    fetch_url = f'{authserver_url}/.well-known/oauth-authorization-server'

    with httpx.Client(timeout=timeout) as client:
        response = client.get(fetch_url)
        response.raise_for_status()

        metadata_dict = response.json()

        # Validate against ATProto requirements
        try:
            validate_authserver_metadata(metadata_dict, fetch_url)
        except ValueError as e:
            raise UnsupportedAuthServerError(str(e)) from e

        # Parse into model
        return AuthServerMetadata(
            issuer=metadata_dict['issuer'],
            authorization_endpoint=metadata_dict['authorization_endpoint'],
            token_endpoint=metadata_dict['token_endpoint'],
            pushed_authorization_request_endpoint=metadata_dict['pushed_authorization_request_endpoint'],
            response_types_supported=metadata_dict['response_types_supported'],
            grant_types_supported=metadata_dict['grant_types_supported'],
            code_challenge_methods_supported=metadata_dict['code_challenge_methods_supported'],
            token_endpoint_auth_methods_supported=metadata_dict['token_endpoint_auth_methods_supported'],
            token_endpoint_auth_signing_alg_values_supported=metadata_dict[
                'token_endpoint_auth_signing_alg_values_supported'
            ],
            scopes_supported=metadata_dict['scopes_supported'],
            dpop_signing_alg_values_supported=metadata_dict['dpop_signing_alg_values_supported'],
            authorization_response_iss_parameter_supported=metadata_dict[
                'authorization_response_iss_parameter_supported'
            ],
            require_pushed_authorization_requests=metadata_dict['require_pushed_authorization_requests'],
            client_id_metadata_document_supported=metadata_dict['client_id_metadata_document_supported'],
            revocation_endpoint=metadata_dict.get('revocation_endpoint'),
            jwks_uri=metadata_dict.get('jwks_uri'),
            require_request_uri_registration=metadata_dict.get('require_request_uri_registration'),
        )

@dataclass
class AuthServerMetadata:
    """Authorization Server metadata from discovery."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    pushed_authorization_request_endpoint: str
    response_types_supported: t.List[str]
    grant_types_supported: t.List[str]
    code_challenge_methods_supported: t.List[str]
    token_endpoint_auth_methods_supported: t.List[str]
    token_endpoint_auth_signing_alg_values_supported: t.List[str]
    scopes_supported: t.List[str]
    dpop_signing_alg_values_supported: t.List[str]
    authorization_response_iss_parameter_supported: bool
    require_pushed_authorization_requests: bool
    client_id_metadata_document_supported: bool
    revocation_endpoint: t.Optional[str] = None
    jwks_uri: t.Optional[str] = None
    require_request_uri_registration: t.Optional[bool] = None


@dataclass
class OAuthSession:
    """OAuth session with tokens and metadata."""
    did: str
    handle: str
    pds_url: str
    authserver_iss: str
    access_jwt: str
    refresh_jwt: str
    dpop_private_key: 'EllipticCurvePrivateKey'
    dpop_authserver_nonce: str
    scope: str
    dpop_pds_nonce: t.Optional[str] = None
    expires_at: t.Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class OAuthState:
    """OAuth state for CSRF protection during authorization flow."""

    state: str
    pkce_verifier: str
    redirect_uri: str
    scope: str
    authserver_iss: str
    dpop_private_key: 'EllipticCurvePrivateKey'
    dpop_authserver_nonce: str
    did: t.Optional[str] = None
    handle: t.Optional[str] = None
    pds_url: t.Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AuthServerMetadata:
    """Authorization Server metadata from discovery."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    pushed_authorization_request_endpoint: str
    response_types_supported: t.List[str]
    grant_types_supported: t.List[str]
    code_challenge_methods_supported: t.List[str]
    token_endpoint_auth_methods_supported: t.List[str]
    token_endpoint_auth_signing_alg_values_supported: t.List[str]
    scopes_supported: t.List[str]
    dpop_signing_alg_values_supported: t.List[str]
    authorization_response_iss_parameter_supported: bool
    require_pushed_authorization_requests: bool
    client_id_metadata_document_supported: bool
    revocation_endpoint: t.Optional[str] = None
    jwks_uri: t.Optional[str] = None
    require_request_uri_registration: t.Optional[bool] = None