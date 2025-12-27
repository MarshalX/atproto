import contextlib
import logging
import secrets
import time
import typing as t
from urllib.parse import urlencode

import httpx
from atproto_identity.resolver import IdResolver

from atproto_client.client.base import InvokeType

if t.TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

    from atproto_client.request import Response

from atproto_client.client.methods_mixin.dpop import DPoPManager
from atproto_client.client.methods_mixin.pkce import PKCEManager
from atproto_client.client.oauth_session import (
    AuthServerMetadata,
    OAuthSession,
    OAuthState,
    TokenResponse,
    discover_authserver_from_pds,
    fetch_authserver_metadata,
    is_safe_url,
)
from atproto_client.client.session import SessionEvent
from atproto_client.exceptions import OAuthStateError, OAuthTokenError

logger = logging.getLogger(__name__)




class OauthSessionMethodsMixin:
    def __init__(self, *args: t.Any,
                 client_id: t.Optional[str] = None,
                 redirect_uri: t.Optional[str] = None,
                 scope: t.Optional[str] = None,
                 # state_store: StateStore,
                 # session_store: SessionStore,
                 client_secret_key: t.Optional['EllipticCurvePrivateKey'] = None, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        # OAuth configuration (optional - only needed for OAuth flows)
        self._oauth_client_id = client_id
        self._oauth_redirect_uri = redirect_uri
        self._oauth_scope = scope
        self._oauth_client_secret_key = client_secret_key

        # Lazy-initialize OAuth components only when OAuth is configured
        self._oauth_initialized = False
        self._id_resolver: t.Optional[IdResolver] = None
        self._dpop: t.Optional[DPoPManager] = None
        self._pkce: t.Optional[PKCEManager] = None

        self._oauth_session: t.Optional[OAuthSession] = None

    def _ensure_oauth_initialized(self) -> None:
        """Initialize OAuth components on first use."""
        if self._oauth_initialized:
            return

        if not self._oauth_client_id or not self._oauth_redirect_uri or not self._oauth_scope:
            raise ValueError('OAuth not configured. Provide client_id, redirect_uri, and scope.')

        self._id_resolver = IdResolver()
        self._dpop = DPoPManager()
        self._pkce = PKCEManager()
        self._oauth_initialized = True

    def _invoke(self, invoke_type: 'InvokeType', **kwargs: t.Any) -> 'Response':
        """Override _invoke to handle OAuth sessions with DPoP."""
        from atproto_client.client.base import _handle_kwargs

        # Process kwargs the same way as base client (removes input/output_encoding, etc.)
        _handle_kwargs(kwargs)

        # Non-OAuth requests use normal flow
        if not self._oauth_session or not self._is_oauth_session():
            if invoke_type is InvokeType.QUERY:
                return self.request.get(**kwargs)
            return self.request.post(**kwargs)

        # OAuth requests - add DPoP headers with nonce retry
        self._ensure_oauth_initialized()
        url = kwargs.get('url', '')
        headers = kwargs.pop('headers', {})

        # Use PDS nonce for PDS requests (separate from auth server nonce)
        from atproto_client.exceptions import UnauthorizedError

        current_nonce = self._oauth_session.dpop_pds_nonce or ''
        for attempt in range(2):
            logger.info(f"DPoP request attempt {attempt}, nonce: {current_nonce[:20] if current_nonce else 'None'}...")
            dpop_proof = self._dpop.create_proof(
                method='GET' if invoke_type is InvokeType.QUERY else 'POST',
                url=url,
                private_key=self._oauth_session.dpop_private_key,
                nonce=current_nonce if current_nonce else None,
                access_token=self._oauth_session.access_jwt,
            )

            headers['Authorization'] = f'DPoP {self._oauth_session.access_jwt}'
            headers['DPoP'] = dpop_proof

            try:
                if invoke_type is InvokeType.QUERY:
                    response = self.request.get(headers=headers, **kwargs)
                else:
                    response = self.request.post(headers=headers, **kwargs)
            except UnauthorizedError as e:
                # Check if it's a DPoP nonce error that we can retry
                response = e.response
                logger.info(f'DPoP caught UnauthorizedError, status: {response.status_code}')

                is_nonce_error = self._dpop.is_dpop_nonce_error(response)
                logger.info(f'is_nonce_error: {is_nonce_error}')

                if is_nonce_error:
                    new_nonce = self._dpop.extract_nonce_from_response(response)
                    logger.info(f"Extracted nonce: {new_nonce[:20] if new_nonce else 'None'}...")
                    if new_nonce and attempt == 0:
                        current_nonce = new_nonce
                        continue
                # Not a nonce error or can't retry - re-raise
                raise

            is_nonce_error = self._dpop.is_dpop_nonce_error(response)
            if is_nonce_error:
                new_nonce = self._dpop.extract_nonce_from_response(response)
                if new_nonce and attempt == 0:
                    current_nonce = new_nonce
                    continue

            # Update stored PDS nonce
            self._oauth_session.dpop_pds_nonce = (
                self._dpop.extract_nonce_from_response(response) or current_nonce
            )
            return response

        return response

    def _make_token_request(
            self,
            token_url: str,
            params: t.Dict[str, str],
            dpop_key: 'EllipticCurvePrivateKey',
            dpop_nonce: str,
    ) -> t.Tuple[str, httpx.Response]:
        """Make token request with DPoP and client assertion.

        Handles DPoP nonce rotation automatically.

        Returns:
        Tuple of (updated_dpop_nonce, response).
        """
        self._ensure_oauth_initialized()
        if not is_safe_url(token_url):
            raise ValueError(f'Unsafe token URL: {token_url}')

        # Add client authentication
        if self._oauth_client_secret_key:
            # Confidential client - use client assertion
            client_assertion = self._create_client_assertion(token_url)
            params['client_id'] = self._oauth_client_id
            params['client_assertion_type'] = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
            params['client_assertion'] = client_assertion
        else:
            # Public client
            params['client_id'] = self._oauth_client_id

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
            with httpx.Client() as client:
                response = client.post(
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
        if not self._oauth_client_secret_key:
            raise ValueError('Client secret key required for client assertion')

        header = {
            'alg': 'ES256',
            'typ': 'JWT',
        }

        now = int(time.time())
        payload = {
            'iss': self._oauth_client_id,
            'sub': self._oauth_client_id,
            'aud': audience,
            'jti': secrets.token_urlsafe(16),
            'iat': now,
            'exp': now + 60,  # Valid for 60 seconds
        }

        return self._dpop._sign_jwt(header, payload, self._oauth_client_secret_key)

    def start_authorization(
            self,
            handle_or_did: str,
    ) -> t.Tuple[str, str, OAuthState]:
        """Start OAuth authorization flow.

        Args:
        handle_or_did: User handle (e.g., 'user.bsky.social') or DID.

        Returns:
        Tuple of (authorization_url, state) for redirecting user.

        Raises:
        ValueError: If handle/DID resolution fails or URL validation fails.
        OAuthError: If authorization server discovery or PAR fails.
        """
        self._ensure_oauth_initialized()
        # 1. Resolve identity
        if handle_or_did.startswith('did:'):
            # Input is a DID
            did = handle_or_did
        else:
            # Input is a handle - resolve to DID first
            resolved_did = self._id_resolver.handle.resolve(handle_or_did)
            if not resolved_did:
                raise ValueError(f'Failed to resolve handle: {handle_or_did}')
            did = resolved_did

        # 2. Resolve DID to get ATProto data (includes PDS, handle, etc.)
        atproto_data = self._id_resolver.did.resolve_atproto_data(did)

        handle = atproto_data.handle or handle_or_did
        pds_url = atproto_data.pds

        if not pds_url:
            raise ValueError(f'No PDS endpoint found in DID document for {did}')

        # 3. Discover authorization server
        authserver_url = discover_authserver_from_pds(pds_url)
        authserver_url = authserver_url.rstrip('/')

        # 4. Fetch authorization server metadata
        authserver_meta = fetch_authserver_metadata(authserver_url)

        # 5. Generate PKCE verifier and challenge
        pkce_verifier, pkce_challenge = self._pkce.generate_pair()

        # 6. Generate DPoP keypair
        dpop_key = self._dpop.generate_keypair()

        # 7. Generate state token
        state_token = secrets.token_urlsafe(32)

        # 8. Send PAR (Pushed Authorization Request)
        request_uri, dpop_nonce = self._send_par_request(
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
            redirect_uri=self._oauth_redirect_uri,
            scope=self._oauth_scope,
            authserver_iss=authserver_meta.issuer,
            dpop_private_key=dpop_key,
            dpop_authserver_nonce=dpop_nonce,
            did=did,
            handle=handle,
            pds_url=pds_url,
        )

        # 10. Build authorization URL
        auth_params = {
            'client_id': self._oauth_client_id,
            'request_uri': request_uri,
        }
        auth_url = f'{authserver_meta.authorization_endpoint}?{urlencode(auth_params)}'

        if not is_safe_url(auth_url):
            raise ValueError(f'Generated unsafe authorization URL: {auth_url}')

        return auth_url, state_token, oauth_state

    def _exchange_code_for_tokens(
            self,
            code: str,
            oauth_state: OAuthState,
    ) -> t.Tuple[TokenResponse, str]:
        """Exchange authorization code for tokens.

        Returns:
        Tuple of (token_response, dpop_nonce).
        """
        # Fetch metadata again (could have changed)
        authserver_meta = fetch_authserver_metadata(oauth_state.authserver_iss)

        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'code_verifier': oauth_state.pkce_verifier,
            'redirect_uri': self._oauth_redirect_uri,
        }

        dpop_nonce, response = self._make_token_request(
            token_url=authserver_meta.token_endpoint,
            params=params,
            dpop_key=oauth_state.dpop_private_key,
            dpop_nonce=oauth_state.dpop_authserver_nonce,
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


    def handle_callback(
            self,
            code: str,
            iss: str,
            oauth_state: OAuthState
    ) -> OAuthSession:
        """Handle OAuth callback and complete authorization.

        Args:
            code: Authorization code from callback.
            iss: Issuer parameter from callback.
            oauth_state: OAuth state object from start_authorization.

        Returns:
            OAuth session with tokens.

        Raises:
            OAuthStateError: If state validation fails.
        OAuthTokenError: If token exchange fails.
        """
        # 1. Retrieve and verify state
        if not oauth_state:
            raise OAuthStateError('Invalid or expired state parameter')

        if oauth_state.authserver_iss != iss:
            raise OAuthStateError(f'Issuer mismatch: expected {oauth_state.authserver_iss}, got {iss}')

        # 2. Exchange code for tokens
        token_response, dpop_nonce = self._exchange_code_for_tokens(
            code=code,
            oauth_state=oauth_state,
        )

        # 3. Verify token response
        if token_response.sub != oauth_state.did:
            raise OAuthTokenError(f'DID mismatch in token: expected {oauth_state.did}, got {token_response.sub}')

        if token_response.scope != self._oauth_scope:
            raise OAuthTokenError(f'Scope mismatch: expected {self._oauth_scope}, got {token_response.scope}')

        # 4. Create and store session
        session = OAuthSession(
            did=oauth_state.did or token_response.sub,
            handle=oauth_state.handle or '',
            pds_url=oauth_state.pds_url or '',
            authserver_iss=oauth_state.authserver_iss,
            access_jwt=token_response.access_token,
            refresh_jwt=token_response.refresh_token or '',
            dpop_private_key=oauth_state.dpop_private_key,
            dpop_authserver_nonce=dpop_nonce,
            scope=token_response.scope,
        )

        self._set_oauth_session(SessionEvent.CREATE, session)

        return session

    def _send_par_request(self,
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
            'redirect_uri': self._oauth_redirect_uri,
            'scope': self._oauth_scope,
            'login_hint': login_hint,
        }

        # Make PAR request with DPoP
        dpop_nonce, response = self._make_token_request(
            token_url=par_url,
            params=params,
            dpop_key=dpop_key,
            dpop_nonce='',  # Initial request has no nonce
        )

        if response.status_code not in (200, 201):
            raise OAuthTokenError(f'PAR request failed: {response.status_code} {response.text}')

        par_response = response.json()
        return par_response['request_uri'], dpop_nonce


    def refresh_session(self, session: OAuthSession) -> OAuthSession:
        """Refresh OAuth session tokens.

        Args:
        session: Current OAuth session.

        Returns:
        Updated OAuth session with new tokens.

        Raises:
        OAuthTokenError: If token refresh fails.
        """
        # Fetch current auth server metadata
        authserver_meta = fetch_authserver_metadata(session.authserver_iss)

        # Prepare refresh token request
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': session.refresh_jwt,
        }

        # Make token request with DPoP
        dpop_nonce, response = self._make_token_request(
            token_url=authserver_meta.token_endpoint,
            params=params,
            dpop_key=session.dpop_private_key,
            dpop_nonce=session.dpop_authserver_nonce,
        )

        if response.status_code not in (200, 201):
            raise OAuthTokenError(f'Token refresh failed: {response.status_code} {response.text}')

        token_data = response.json()
        token_response = TokenResponse(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            scope=token_data['scope'],
            sub=token_data['sub'],
            refresh_token=token_data.get('refresh_token', session.refresh_jwt),
            expires_in=token_data.get('expires_in'),
        )

        # Update session
        session.access_jwt = token_response.access_token
        session.refresh_jwt = token_response.refresh_token
        session.dpop_authserver_nonce = dpop_nonce

        return session

    def revoke_session(self, session: OAuthSession) -> None:
        """Revoke OAuth session tokens.

        Args:
        session: OAuth session to revoke.
        """
        authserver_meta = fetch_authserver_metadata(session.authserver_iss)

        if not authserver_meta.revocation_endpoint:
            # Revocation not supported
            return

        # Revoke both access and refresh tokens
        for token_type in ['access_token', 'refresh_token']:
            token = session.access_jwt if token_type == 'access_token' else session.refresh_jwt  # noqa: S105 - token type identifier, not a password
            if not token:
                continue

            params = {
                'token': token,
                'token_type_hint': token_type,
            }

            # Best-effort revocation; failures are intentionally silent
            with contextlib.suppress(OAuthTokenError, ValueError):
                self._make_token_request(
                    token_url=authserver_meta.revocation_endpoint,
                    params=params,
                    dpop_key=session.dpop_private_key,
                    dpop_nonce=session.dpop_authserver_nonce,
                )


    def import_oauth_session(self, session: OAuthSession) -> None:
        self._set_oauth_session(SessionEvent.IMPORT, session)
        self._ensure_oauth_initialized()

    def _set_oauth_session(self, event: SessionEvent, session: OAuthSession) -> None:
        # Update base URL to PDS so all requests go through PDS (which proxies to AppView)
        self.update_base_url(session.pds_url)

        if not self._oauth_session:
            self._oauth_session = OAuthSession(
                access_jwt=session.access_jwt,
                refresh_jwt=session.refresh_jwt,
                did=session.did,
                authserver_iss=session.authserver_iss,
                handle=session.handle,
                pds_url=session.pds_url,
                dpop_private_key=session.dpop_private_key,
                dpop_authserver_nonce=session.dpop_authserver_nonce,
                scope=session.scope,
                dpop_pds_nonce=session.dpop_pds_nonce,
                expires_at=session.expires_at,
                created_at=session.created_at
            )

        else:
            logger.info('_set_oauth_session: session {}'.format(self._oauth_session))
            self._oauth_session.access_jwt = session.access_jwt
            self._oauth_session.refresh_jwt = session.refresh_jwt
            self._oauth_session.authserver_iss = session.authserver_iss
            self._oauth_session.did = session.did
            self._oauth_session.handle = session.handle
            self._oauth_session.pds_url = session.pds_url
            self._oauth_session.dpop_private_key = session.dpop_private_key
            self._oauth_session.dpop_authserver_nonce = session.dpop_authserver_nonce
            self._oauth_session.scope = session.scope
            self._oauth_session.dpop_pds_nonce = session.dpop_pds_nonce
            self._oauth_session.expires_at = session.expires_at
            self._oauth_session.created_at = session.created_at

    def _is_oauth_session(self) -> bool:
        return self._oauth_session is not None
