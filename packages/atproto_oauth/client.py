"""ATProto OAuth 2.1 client implementation."""

import secrets
import time
import typing as t
from urllib.parse import urlencode

import httpx
from atproto_identity.resolver import AsyncIdResolver

from atproto_oauth.dpop import DPoPManager
from atproto_oauth.exceptions import OAuthStateError, OAuthTokenError
from atproto_oauth.metadata import (
    discover_authserver_from_pds_async,
    fetch_authserver_metadata_async,
)
from atproto_oauth.models import AuthServerMetadata, OAuthSession, OAuthState, TokenResponse
from atproto_oauth.pkce import PKCEManager
from atproto_oauth.security import is_safe_url
from atproto_oauth.stores.base import SessionStore, StateStore

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


class OAuthClient:
    """ATProto OAuth 2.1 client.

    Implements complete OAuth authorization code flow with PKCE and DPoP.

    Args:
        client_id: OAuth client ID (must be HTTPS URL or localhost).
        redirect_uri: OAuth redirect URI.
        scope: OAuth scopes (space-separated).
        state_store: Store for temporary OAuth state.
        session_store: Store for OAuth sessions.
        client_secret_key: Optional EC private key for confidential clients.
        client_secret_kid: Key ID for the client secret key (required if client_secret_key is provided).
    """

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        state_store: StateStore,
        session_store: SessionStore,
        client_secret_key: t.Optional['EllipticCurvePrivateKey'] = None,
        client_secret_kid: t.Optional[str] = None,
    ) -> None:
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state_store = state_store
        self.session_store = session_store
        self.client_secret_key = client_secret_key
        self.client_secret_kid = client_secret_kid

        self._id_resolver = AsyncIdResolver()
        self._dpop = DPoPManager()
        self._pkce = PKCEManager()

    async def start_authorization(
        self,
        handle_or_did: str,
    ) -> t.Tuple[str, str]:
        """Start OAuth authorization flow.

        Args:
            handle_or_did: User handle (e.g., 'user.bsky.social') or DID.

        Returns:
            Tuple of (authorization_url, state) for redirecting user.

        Raises:
            ValueError: If handle/DID resolution fails or URL validation fails.
            OAuthError: If authorization server discovery or PAR fails.
        """
        # 1. Resolve identity
        if handle_or_did.startswith('did:'):
            # Input is a DID
            did = handle_or_did
        else:
            # Input is a handle - resolve to DID first
            resolved_did = await self._id_resolver.handle.resolve(handle_or_did)
            if not resolved_did:
                raise ValueError(f'Failed to resolve handle: {handle_or_did}')
            did = resolved_did

        # 2. Resolve DID to get ATProto data (includes PDS, handle, etc.)
        atproto_data = await self._id_resolver.did.resolve_atproto_data(did)

        handle = atproto_data.handle or handle_or_did
        pds_url = atproto_data.pds

        if not pds_url:
            raise ValueError(f'No PDS endpoint found in DID document for {did}')

        # 3. Discover authorization server
        authserver_url = await discover_authserver_from_pds_async(pds_url)
        authserver_url = authserver_url.rstrip('/')

        # 4. Fetch authorization server metadata
        authserver_meta = await fetch_authserver_metadata_async(authserver_url)

        # 5. Generate PKCE verifier and challenge
        pkce_verifier, pkce_challenge = self._pkce.generate_pair()

        # 6. Generate DPoP keypair
        dpop_key = self._dpop.generate_keypair()

        # 7. Generate state token
        state_token = secrets.token_urlsafe(32)

        # 8. Send PAR (Pushed Authorization Request)
        request_uri, dpop_nonce = await self._send_par_request(
            authserver_meta=authserver_meta,
            login_hint=handle_or_did,
            pkce_challenge=pkce_challenge,
            dpop_key=dpop_key,
            state=state_token,
        )

        # 9. Store state
        oauth_state = OAuthState(
            state=state_token,
            pkce_verifier=pkce_verifier,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            authserver_iss=authserver_meta.issuer,
            dpop_private_key=dpop_key,
            dpop_authserver_nonce=dpop_nonce,
            did=did,
            handle=handle,
            pds_url=pds_url,
        )
        await self.state_store.save_state(oauth_state)

        # 10. Build authorization URL
        auth_params = {
            'client_id': self.client_id,
            'request_uri': request_uri,
        }
        auth_url = f'{authserver_meta.authorization_endpoint}?{urlencode(auth_params)}'

        if not is_safe_url(auth_url):
            raise ValueError(f'Generated unsafe authorization URL: {auth_url}')

        return auth_url, state_token

    async def handle_callback(
        self,
        code: str,
        state: str,
        iss: str,
    ) -> OAuthSession:
        """Handle OAuth callback and complete authorization.

        Args:
            code: Authorization code from callback.
            state: State parameter from callback.
            iss: Issuer parameter from callback.

        Returns:
            OAuth session with tokens.

        Raises:
            OAuthStateError: If state validation fails.
            OAuthTokenError: If token exchange fails.
        """
        # 1. Retrieve and verify state
        oauth_state = await self.state_store.get_state(state)
        if not oauth_state:
            raise OAuthStateError('Invalid or expired state parameter')

        if oauth_state.authserver_iss != iss:
            raise OAuthStateError(f'Issuer mismatch: expected {oauth_state.authserver_iss}, got {iss}')

        # Delete state (one-time use)
        await self.state_store.delete_state(state)

        # 2. Exchange code for tokens
        token_response, dpop_nonce = await self._exchange_code_for_tokens(
            code=code,
            oauth_state=oauth_state,
        )

        # 3. Verify token response
        if token_response.sub != oauth_state.did:
            raise OAuthTokenError(f'DID mismatch in token: expected {oauth_state.did}, got {token_response.sub}')

        if token_response.scope != self.scope:
            raise OAuthTokenError(f'Scope mismatch: expected {self.scope}, got {token_response.scope}')

        # 4. Create and store session
        session = OAuthSession(
            did=oauth_state.did or token_response.sub,
            handle=oauth_state.handle or '',
            pds_url=oauth_state.pds_url or '',
            authserver_iss=oauth_state.authserver_iss,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token or '',
            dpop_private_key=oauth_state.dpop_private_key,
            dpop_authserver_nonce=dpop_nonce,
            scope=token_response.scope,
        )

        await self.session_store.save_session(session)

        return session

    async def refresh_session(self, session: OAuthSession) -> OAuthSession:
        """Refresh OAuth session tokens.

        Args:
            session: Current OAuth session.

        Returns:
            Updated OAuth session with new tokens.

        Raises:
            OAuthTokenError: If token refresh fails.
        """
        # Fetch current auth server metadata
        authserver_meta = await fetch_authserver_metadata_async(session.authserver_iss)

        # Prepare refresh token request
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': session.refresh_token,
        }

        # Make token request with DPoP
        dpop_nonce, response = await self._make_token_request(
            token_url=authserver_meta.token_endpoint,
            params=params,
            dpop_key=session.dpop_private_key,
            dpop_nonce=session.dpop_authserver_nonce,
            issuer=authserver_meta.issuer,
        )

        if response.status_code not in (200, 201):
            raise OAuthTokenError(f'Token refresh failed: {response.status_code} {response.text}')

        token_data = response.json()
        token_response = TokenResponse(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            scope=token_data['scope'],
            sub=token_data['sub'],
            refresh_token=token_data.get('refresh_token', session.refresh_token),
            expires_in=token_data.get('expires_in'),
        )

        # Update session
        session.access_token = token_response.access_token
        session.refresh_token = token_response.refresh_token
        session.dpop_authserver_nonce = dpop_nonce

        await self.session_store.save_session(session)

        return session

    async def revoke_session(self, session: OAuthSession) -> None:
        """Revoke OAuth session tokens.

        Args:
            session: OAuth session to revoke.
        """
        authserver_meta = await fetch_authserver_metadata_async(session.authserver_iss)

        if not authserver_meta.revocation_endpoint:
            # Revocation not supported, just delete local session
            await self.session_store.delete_session(session.did)
            return

        # Revoke both access and refresh tokens
        for token_type in ['access_token', 'refresh_token']:
            token = session.access_token if token_type == 'access_token' else session.refresh_token
            if not token:
                continue

            params = {
                'token': token,
                'token_type_hint': token_type,
            }

            try:
                await self._make_token_request(
                    token_url=authserver_meta.revocation_endpoint,
                    params=params,
                    dpop_key=session.dpop_private_key,
                    dpop_nonce=session.dpop_authserver_nonce,
                    issuer=authserver_meta.issuer,
                )
            except (OAuthTokenError, ValueError):
                # Best-effort revocation; failures are intentionally silent
                pass

        # Delete local session
        await self.session_store.delete_session(session.did)

    async def make_authenticated_request(
        self,
        session: OAuthSession,
        method: str,
        url: str,
        **kwargs: t.Any,
    ) -> httpx.Response:
        """Make authenticated request to PDS with DPoP.

        Args:
            session: OAuth session.
            method: HTTP method.
            url: Request URL.
            **kwargs: Additional request arguments.

        Returns:
            HTTP response.
        """
        if not is_safe_url(url):
            raise ValueError(f'Unsafe URL: {url}')

        # Try request with retry for DPoP nonce
        for attempt in range(2):
            # Create DPoP proof
            dpop_proof = self._dpop.create_proof(
                method=method.upper(),
                url=url,
                private_key=session.dpop_private_key,
                nonce=session.dpop_pds_nonce,
                access_token=session.access_token,
            )

            # Add auth headers
            headers = kwargs.pop('headers', {})
            headers['Authorization'] = f'DPoP {session.access_token}'
            headers['DPoP'] = dpop_proof

            # Make request
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, headers=headers, **kwargs)

            # Check for DPoP nonce error
            if self._dpop.is_dpop_nonce_error(response):
                new_nonce = self._dpop.extract_nonce_from_response(response)
                if new_nonce and attempt == 0:
                    session.dpop_pds_nonce = new_nonce
                    await self.session_store.save_session(session)
                    continue  # Retry with new nonce

            return response

        return response

    async def _send_par_request(
        self,
        authserver_meta: AuthServerMetadata,
        login_hint: str,
        pkce_challenge: str,
        dpop_key: 'EllipticCurvePrivateKey',
        state: str,
    ) -> t.Tuple[str, str]:
        """Send Pushed Authorization Request.

        Returns:
            Tuple of (request_uri, dpop_nonce).
        """
        par_url = authserver_meta.pushed_authorization_request_endpoint

        params = {
            'response_type': 'code',
            'code_challenge': pkce_challenge,
            'code_challenge_method': 'S256',
            'state': state,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'login_hint': login_hint,
        }

        # Make PAR request with DPoP
        dpop_nonce, response = await self._make_token_request(
            token_url=par_url,
            params=params,
            dpop_key=dpop_key,
            dpop_nonce='',  # Initial request has no nonce
            issuer=authserver_meta.issuer,
        )

        if response.status_code not in (200, 201):
            raise OAuthTokenError(f'PAR request failed: {response.status_code} {response.text}')

        par_response = response.json()
        return par_response['request_uri'], dpop_nonce

    async def _exchange_code_for_tokens(
        self,
        code: str,
        oauth_state: OAuthState,
    ) -> t.Tuple[TokenResponse, str]:
        """Exchange authorization code for tokens.

        Returns:
            Tuple of (token_response, dpop_nonce).
        """
        # Fetch metadata again (could have changed)
        authserver_meta = await fetch_authserver_metadata_async(oauth_state.authserver_iss)

        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'code_verifier': oauth_state.pkce_verifier,
            'redirect_uri': self.redirect_uri,
        }

        dpop_nonce, response = await self._make_token_request(
            token_url=authserver_meta.token_endpoint,
            params=params,
            dpop_key=oauth_state.dpop_private_key,
            dpop_nonce=oauth_state.dpop_authserver_nonce,
            issuer=authserver_meta.issuer,
        )

        if response.status_code not in (200, 201):
            raise OAuthTokenError(f'Token exchange failed: {response.status_code} {response.text}')

        token_data = response.json()
        token_response = TokenResponse(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            scope=token_data['scope'],
            sub=token_data['sub'],
            refresh_token=token_data.get('refresh_token'),
            expires_in=token_data.get('expires_in'),
        )

        return token_response, dpop_nonce

    async def _make_token_request(
        self,
        token_url: str,
        params: t.Dict[str, str],
        dpop_key: 'EllipticCurvePrivateKey',
        dpop_nonce: str,
        issuer: t.Optional[str] = None,
    ) -> t.Tuple[str, httpx.Response]:
        """Make token request with DPoP and client assertion.

        Handles DPoP nonce rotation automatically.

        Args:
            token_url: The token endpoint URL.
            params: Request parameters.
            dpop_key: DPoP private key.
            dpop_nonce: Current DPoP nonce.
            issuer: Authorization server issuer (required for confidential clients).
                    Per ATProto OAuth spec, the aud claim must be the issuer.

        Returns:
            Tuple of (updated_dpop_nonce, response).
        """
        if not is_safe_url(token_url):
            raise ValueError(f'Unsafe token URL: {token_url}')

        # Add client authentication
        if self.client_secret_key:
            # Confidential client - use client assertion
            # Per ATProto OAuth spec: "The aud claim (audience) of the client
            # assertion JWT must be the Authorization Server's issuer."
            if not issuer:
                raise ValueError('issuer required for confidential client authentication')
            client_assertion = self._create_client_assertion(issuer)
            params['client_id'] = self.client_id
            params['client_assertion_type'] = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
            params['client_assertion'] = client_assertion
        else:
            # Public client
            params['client_id'] = self.client_id

        # Try request with DPoP nonce retry
        current_nonce = dpop_nonce
        for attempt in range(2):
            # Create DPoP proof
            dpop_proof = self._dpop.create_proof(
                method='POST',
                url=token_url,
                private_key=dpop_key,
                nonce=current_nonce if current_nonce else None,
            )

            # Make request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    token_url,
                    data=params,
                    headers={'DPoP': dpop_proof},
                )

            # Check for DPoP nonce error
            if self._dpop.is_dpop_nonce_error(response):
                new_nonce = self._dpop.extract_nonce_from_response(response)
                if new_nonce and attempt == 0:
                    current_nonce = new_nonce
                    continue  # Retry with new nonce

            # Extract final nonce
            final_nonce = self._dpop.extract_nonce_from_response(response) or current_nonce

            return final_nonce, response

        return current_nonce, response

    def _create_client_assertion(self, audience: str) -> str:
        """Create client assertion JWT for confidential client."""
        if not self.client_secret_key:
            raise ValueError('Client secret key required for client assertion')
        if not self.client_secret_kid:
            raise ValueError('Client secret kid required for client assertion')

        header = {
            'alg': 'ES256',
            'typ': 'JWT',
            'kid': self.client_secret_kid,
        }

        now = int(time.time())
        payload = {
            'iss': self.client_id,
            'sub': self.client_id,
            'aud': audience,
            'jti': secrets.token_urlsafe(16),
            'iat': now,
            'exp': now + 60,  # Valid for 60 seconds
        }

        return self._dpop._sign_jwt(header, payload, self.client_secret_key)
