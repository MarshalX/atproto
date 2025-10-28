"""OAuth data models."""

import typing as t
from dataclasses import dataclass, field
from datetime import datetime, timezone

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


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
class OAuthSession:
    """OAuth session with tokens and metadata."""

    did: str
    handle: str
    pds_url: str
    authserver_iss: str
    access_token: str
    refresh_token: str
    dpop_private_key: 'EllipticCurvePrivateKey'
    dpop_authserver_nonce: str
    scope: str
    dpop_pds_nonce: t.Optional[str] = None
    expires_at: t.Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TokenResponse:
    """Token response from authorization server."""

    access_token: str
    token_type: str
    scope: str
    sub: str  # DID
    refresh_token: t.Optional[str] = None
    expires_in: t.Optional[int] = None
