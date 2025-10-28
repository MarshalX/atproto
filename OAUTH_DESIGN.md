# ATProto Python SDK OAuth Implementation Design

## Overview

implementing comprehensive OAuth 2.1 support for the atproto Python SDK, following the [atproto OAuth specification](https://atproto.com/specs/oauth).

## Key Requirements

### OAuth 2.1 Mandatory Features
- ✅ Authorization code grant only
- ✅ PKCE (Proof Key for Code Exchange) with S256
- ✅ DPoP (Demonstrating Proof-of-Possession) with ES256
- ✅ PAR (Pushed Authorization Requests)
- ✅ Server-issued DPoP nonces (mandatory rotation)
- ✅ Client metadata document (for confidential clients)

### ATProto-Specific Requirements
- ✅ DID-based authentication
- ✅ Handle/DID bidirectional resolution
- ✅ PDS endpoint discovery from DID documents
- ✅ Authorization server discovery from PDS
- ✅ Client ID must be HTTPS URL (or localhost for development)

## Architecture

### New Package: `atproto_oauth`

```
packages/atproto_oauth/
├── __init__.py
├── client.py              # Main OAuth client (sync + async)
├── models.py              # Data models (OAuthSession, OAuthState, etc.)
├── dpop.py                # DPoP JWT generation and validation
├── pkce.py                # PKCE code verifier/challenge generation
├── security.py            # Security utilities (URL validation, etc.)
├── stores/
│   ├── __init__.py
│   ├── base.py            # Abstract base classes
│   ├── memory.py          # In-memory stores (dev only)
│   └── session_store.py   # Session management
├── metadata.py            # Client metadata and server discovery
└── exceptions.py          # OAuth-specific exceptions
```

### Integration with Existing Packages

#### `atproto_identity`
- Already has handle/DID resolution ✅
- Need to add: PDS endpoint extraction from DID docs
- Need to add: Bidirectional handle verification

#### `atproto_crypto`
- Already has ES256 (P256) support ✅
- Will use for DPoP key generation

#### `atproto_client`
- Update `Session` class to support OAuth sessions
- Add OAuth login methods to `Client`/`AsyncClient`
- Maintain backward compatibility with password auth

## Core Components

### 1. OAuth Models (`models.py`)

```python
@dataclass
class OAuthState:
    """OAuth state for CSRF protection."""
    state: str
    pkce_verifier: str
    redirect_uri: str
    scope: str
    authserver_iss: str
    dpop_private_jwk: JsonWebKey
    dpop_authserver_nonce: str
    did: Optional[str]
    handle: Optional[str]
    pds_url: Optional[str]
    created_at: datetime

@dataclass
class OAuthSession:
    """OAuth session with tokens and metadata."""
    did: str
    handle: str
    pds_url: str
    authserver_iss: str
    access_token: str
    refresh_token: str
    dpop_private_jwk: JsonWebKey
    dpop_authserver_nonce: str
    dpop_pds_nonce: Optional[str]
    scope: str
    expires_at: Optional[datetime]

@dataclass
class AuthServerMetadata:
    """Authorization Server metadata."""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    pushed_authorization_request_endpoint: str
    revocation_endpoint: Optional[str]
    dpop_signing_alg_values_supported: List[str]
    # ... other fields from OAuth metadata
```

### 2. DPoP Implementation (`dpop.py`)

```python
class DPoPManager:
    """Manages DPoP proof generation for OAuth."""

    @staticmethod
    def generate_keypair() -> JsonWebKey:
        """Generate ES256 keypair for DPoP."""

    @staticmethod
    def create_proof(
        method: str,
        url: str,
        dpop_private_jwk: JsonWebKey,
        nonce: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> str:
        """Generate DPoP proof JWT."""

    @staticmethod
    def extract_nonce_from_response(response: httpx.Response) -> Optional[str]:
        """Extract DPoP nonce from error response."""
```

### 3. PKCE Implementation (`pkce.py`)

```python
class PKCEManager:
    """Manages PKCE code verifier and challenge generation."""

    @staticmethod
    def generate_verifier(length: int = 128) -> str:
        """Generate code verifier."""

    @staticmethod
    def generate_challenge(verifier: str) -> str:
        """Generate S256 code challenge."""
```

### 4. Session Store (`stores/`)

```python
class StateStore(ABC):
    """Abstract state store for OAuth flow."""

    @abstractmethod
    async def save_state(self, state: OAuthState) -> None: ...

    @abstractmethod
    async def get_state(self, state_key: str) -> Optional[OAuthState]: ...

    @abstractmethod
    async def delete_state(self, state_key: str) -> None: ...

class SessionStore(ABC):
    """Abstract session store for OAuth sessions."""

    @abstractmethod
    async def save_session(self, session: OAuthSession) -> None: ...

    @abstractmethod
    async def get_session(self, did: str) -> Optional[OAuthSession]: ...

    @abstractmethod
    async def delete_session(self, did: str) -> None: ...
```

### 5. OAuth Client (`client.py`)

```python
class OAuthClient:
    """ATProto OAuth 2.1 client."""

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        state_store: StateStore,
        session_store: SessionStore,
        client_secret_jwk: Optional[JsonWebKey] = None,  # For confidential clients
    ):
        ...

    async def start_authorization(
        self,
        handle_or_did: str,
    ) -> Tuple[str, str]:
        """
        Start OAuth authorization flow.

        Returns:
            (authorization_url, state)
        """
        # 1. Resolve identity (handle -> DID)
        # 2. Get PDS endpoint from DID doc
        # 3. Discover authorization server
        # 4. Fetch auth server metadata
        # 5. Generate PKCE verifier/challenge
        # 6. Generate DPoP keypair
        # 7. Send PAR request
        # 8. Store state
        # 9. Return authorization URL

    async def handle_callback(
        self,
        code: str,
        state: str,
        iss: str,
    ) -> OAuthSession:
        """
        Handle OAuth callback and complete authorization.

        Returns:
            OAuthSession with tokens
        """
        # 1. Verify state parameter
        # 2. Retrieve stored state
        # 3. Exchange code for tokens
        # 4. Verify response
        # 5. Create and store session
        # 6. Return session

    async def refresh_session(
        self,
        session: OAuthSession,
    ) -> OAuthSession:
        """Refresh OAuth session tokens."""
        # 1. Fetch auth server metadata
        # 2. Create client assertion
        # 3. Create DPoP proof
        # 4. POST to token endpoint
        # 5. Handle DPoP nonce rotation
        # 6. Update session
        # 7. Return updated session

    async def revoke_session(
        self,
        session: OAuthSession,
    ) -> None:
        """Revoke OAuth session tokens."""

    async def make_authenticated_request(
        self,
        session: OAuthSession,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """Make authenticated request to PDS with DPoP."""
        # 1. Create DPoP proof for request
        # 2. Add Authorization + DPoP headers
        # 3. Send request
        # 4. Handle DPoP nonce rotation if needed
        # 5. Return response
```

### 6. Client Integration (`atproto_client`)

```python
# Update Session class
@dataclass
class Session:
    handle: str
    did: str
    access_jwt: Optional[str] = None  # For password auth
    refresh_jwt: Optional[str] = None  # For password auth
    pds_endpoint: Optional[str] = 'https://bsky.social'

    # OAuth fields (mutually exclusive with password auth)
    oauth_session: Optional[OAuthSession] = None

# Add methods to Client/AsyncClient
class AsyncClient:
    async def login_oauth_start(
        self,
        handle_or_did: str,
        client_id: str,
        redirect_uri: str,
        scope: str = "atproto",
    ) -> Tuple[str, str]:
        """Start OAuth login flow."""

    async def login_oauth_complete(
        self,
        code: str,
        state: str,
        iss: str,
    ) -> Session:
        """Complete OAuth login flow."""

    async def login_oauth_session(
        self,
        oauth_session: OAuthSession,
    ) -> Session:
        """Login with existing OAuth session."""
```

## Comparison with Nick's PR #589

### What Nick Implemented ✅
- DPoP support in Session class
- Static token fields (access_token, dpop_token, dpop_jwk)
- DPoP JWT generation in request headers
- Basic DPoP nonce handling

### What Nick Didn't Implement ❌
- Full OAuth authorization flow
- PKCE support
- PAR (Pushed Authorization Requests)
- State management
- Token refresh with OAuth
- Client metadata
- Authorization server discovery
- Bidirectional identity verification

### What We're Adding
- Complete OAuth 2.1 client implementation
- Proper state/session stores
- Full PKCE + DPoP integration
- Client assertion for confidential clients
- Comprehensive error handling
- Production-ready security measures
- Sync + async support throughout

## Comparison with Cookbook

### What We're Adopting from Cookbook ✅
- PAR request implementation
- DPoP nonce rotation logic
- Client assertion JWT generation
- Auth server metadata validation
- Security checks (URL validation, SSRF protection)

### What We're Improving
- Pythonic API design (dataclasses, type hints)
- Async-first with sync wrappers
- Integration with existing SDK
- Pluggable state/session stores
- Better separation of concerns
- Comprehensive error handling

## Implementation Plan

### Phase 1: Core OAuth Components
1. Create `atproto_oauth` package
2. Implement PKCE manager
3. Implement DPoP manager
4. Implement OAuth models
5. Implement security utilities

### Phase 2: OAuth Client
1. Implement state/session stores (memory-based)
2. Implement authorization server discovery
3. Implement OAuth client with full flow
4. Add sync wrappers

### Phase 3: Integration
1. Update Session class in atproto_client
2. Add OAuth login methods to Client/AsyncClient
3. Update request handling for OAuth

### Phase 4: Examples & Testing
1. Create Flask example app
2. Write comprehensive tests
3. Update documentation
4. Create migration guide

## Security Considerations

### SSRF Protection
- Validate all URLs before making requests
- Use hardened HTTP client with timeouts
- Restrict to HTTPS (except localhost)

### DPoP Nonce Handling
- Automatic retry with new nonce
- Store nonces per server
- Validate nonce freshness

### State Management
- Generate cryptographically secure state tokens
- Time-limited state storage
- Single-use state tokens

### Token Storage
- Never log tokens
- Secure session storage
- Support for encrypted storage backends

## Backward Compatibility

### Password Auth (Existing)
```python
client = AsyncClient()
await client.login("handle", "password")
```

### OAuth Auth (New)
```python
client = AsyncClient()
auth_url, state = await client.login_oauth_start(
    "handle.bsky.social",
    client_id="https://myapp.com/client-metadata.json",
    redirect_uri="https://myapp.com/callback",
)
# User completes auth in browser
await client.login_oauth_complete(code, state, iss)
```

Both will create a `Session` object that works transparently with the rest of the SDK.

## Open Questions

1. **Session Storage**: Should we provide a default persistent store (SQLite)?
2. **Client Types**: Should we support both confidential and public clients, or just confidential?
3. **Scope Management**: Should we have helpers for common scope patterns?
4. **Token Refresh**: Should it be automatic or manual?
5. **Multi-tenant**: How to handle multiple OAuth sessions in same process?

## Success Criteria

- [ ] Full OAuth 2.1 compliance
- [ ] ATProto OAuth spec compliance
- [ ] Works with Bluesky PDS
- [ ] Works with custom PDS instances
- [ ] Comprehensive test coverage
- [ ] Clear documentation and examples
- [ ] Backward compatible with password auth
- [ ] Production-ready error handling
- [ ] Security best practices followed
