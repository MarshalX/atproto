import contextlib
import random
import threading
import time
import typing as t
from dataclasses import dataclass

import typing_extensions as te
from atproto_crypto.jwk import generate_p256_jwk

from atproto_oauth import _flow
from atproto_oauth._effects import Flow, Sleep, call
from atproto_oauth.dpop import DpopKey, NonceCache, generate_nonce, is_auth_server_nonce_error
from atproto_oauth.exceptions import (
    AuthMethodUnsatisfiableError,
    OAuthCallbackError,
    OAuthError,
    OAuthResponseError,
    TokenInvalidError,
    TokenRefreshError,
    TokenRevokedError,
)
from atproto_oauth.keys import Keyset
from atproto_oauth.metadata import (
    ATPROTO_SCOPE,
    DEFAULT_LOOPBACK_REDIRECT_URIS,
    AuthServerMetadata,
    ClientMetadata,
    build_client_metadata,
    build_loopback_client_id,
    validate_client_metadata,
)
from atproto_oauth.models import AuthMethod, OAuthSessionData, OAuthStateData, TokenSet
from atproto_oauth.pkce import generate_pkce
from atproto_oauth.security import HttpResponse, get_origin

if t.TYPE_CHECKING:
    from atproto_crypto.jwk import Jwk

    from atproto_oauth._flow import RefreshMode

DEFAULT_STATE_TTL: t.Final = 3600.0
DEFAULT_MAX_PENDING_AUTHORIZATIONS: t.Final = 10_000
# pause before checking whether another process refreshed the tokens first
CONCURRENT_REFRESH_DELAY: t.Final = 1.0

SessionT = t.TypeVar('SessionT')
LockT = t.TypeVar('LockT')


@dataclass(frozen=True)
class OAuthCallbackResult(t.Generic[SessionT]):
    """Outcome of a completed authorization.

    Attributes:
        session: Session of the account that authorized the client.
        state: Application state passed to ``authorize``.
    """

    session: SessionT
    state: t.Optional[str] = None


@dataclass(frozen=True)
class NewSession:
    """Session issued by the authorization server that is not stored yet."""

    data: OAuthSessionData
    server: AuthServerMetadata
    key: DpopKey
    app_state: t.Optional[str]

    @property
    def did(self) -> str:
        return self.data.token_set.sub


class KeyedLocks(t.Generic[LockT]):
    """One lock per key, dropped when nobody holds or waits for it."""

    def __init__(self, lock_factory: t.Callable[[], LockT]) -> None:
        self._lock_factory = lock_factory
        self._guard = threading.Lock()
        self._locks: t.Dict[str, t.Tuple[LockT, int]] = {}

    def __len__(self) -> int:
        return len(self._locks)

    def enter(self, key: str) -> LockT:
        with self._guard:
            lock, holders = self._locks.get(key) or (self._lock_factory(), 0)
            self._locks[key] = (lock, holders + 1)

        return lock

    def leave(self, key: str) -> None:
        with self._guard:
            lock, holders = self._locks[key]
            if holders > 1:
                self._locks[key] = (lock, holders - 1)
            else:
                del self._locks[key]


def _as_list(value: t.Union[str, t.Sequence[str]]) -> t.List[str]:
    return [value] if isinstance(value, str) else list(value)


class _OAuthClientBase:
    def __init__(
        self,
        client_metadata: t.Mapping[str, t.Any],
        keys: t.Optional[t.Iterable[t.Mapping[str, t.Any]]],
        state_store: t.Any,
        session_store: t.Any,
        resolver: t.Any,
        http: t.Any,
        lock: t.Optional[t.Callable[[str], t.Any]],
        on_session_updated: t.Optional[t.Callable[[str, OAuthSessionData], t.Any]],
        on_session_deleted: t.Optional[t.Callable[[str, BaseException], t.Any]],
        state_ttl: float,
    ) -> None:
        self._keyset = Keyset(keys)
        self._metadata = validate_client_metadata(client_metadata, self._keyset)
        self._state_store = state_store
        self._session_store = session_store
        self._resolver = resolver
        self._http = http
        self._lock = lock
        self._on_session_updated = on_session_updated
        self._on_session_deleted = on_session_deleted
        self._state_ttl = state_ttl
        self._nonces = NonceCache()

    @classmethod
    def loopback(
        cls,
        redirect_uri: t.Optional[t.Union[str, t.Sequence[str]]] = None,
        scope: str = ATPROTO_SCOPE,
        **kwargs: t.Any,
    ) -> te.Self:
        """Create a public client that needs no hosted metadata. For command line tools and development.

        Args:
            redirect_uri: Redirect URIs on ``http://127.0.0.1`` or ``http://[::1]``.
                The authorization server ignores the port, so it may be picked at run time.
            scope: Scope the client may request.
            **kwargs: Other arguments of the client.
        """
        redirect_uris = _as_list(redirect_uri) if redirect_uri else list(DEFAULT_LOOPBACK_REDIRECT_URIS)
        client_id = build_loopback_client_id(redirect_uris, scope)

        return cls(build_client_metadata(client_id, redirect_uris, scope), **kwargs)

    @classmethod
    def public(
        cls,
        client_id: str,
        redirect_uri: t.Union[str, t.Sequence[str]],
        scope: str,
        metadata: t.Optional[t.Mapping[str, t.Any]] = None,
        **kwargs: t.Any,
    ) -> te.Self:
        """Create a public client.

        Args:
            client_id: URL the client metadata is published at.
            redirect_uri: Redirect URIs.
            scope: Scope the client may request.
            metadata: More client metadata fields, such as ``client_name`` or ``application_type``.
            **kwargs: Other arguments of the client.
        """
        return cls(build_client_metadata(client_id, _as_list(redirect_uri), scope, **dict(metadata or {})), **kwargs)

    @classmethod
    def confidential(
        cls,
        client_id: str,
        redirect_uri: t.Union[str, t.Sequence[str]],
        scope: str,
        keys: t.Iterable[t.Mapping[str, t.Any]],
        metadata: t.Optional[t.Mapping[str, t.Any]] = None,
        **kwargs: t.Any,
    ) -> te.Self:
        """Create a confidential client.

        Args:
            client_id: URL the client metadata is published at.
            redirect_uri: Redirect URIs.
            scope: Scope the client may request.
            keys: Private P-256 JWKs with a ``kid``. The first one signs new sessions;
                keep the older ones for as long as sessions started with them are alive.
            metadata: More client metadata fields, such as ``client_name`` or ``jwks_uri``.
            **kwargs: Other arguments of the client.
        """
        keys = list(keys)
        keyset = Keyset(keys)
        if not len(keyset):
            raise ValueError('A confidential client requires at least one client authentication key')

        client_metadata = build_client_metadata(
            client_id, _as_list(redirect_uri), scope, keyset, **dict(metadata or {})
        )

        return cls(client_metadata, keys=keys, **kwargs)

    @property
    def client_id(self) -> str:
        client_id: str = self._metadata['client_id']
        return client_id

    @property
    def client_metadata(self) -> ClientMetadata:
        """Client metadata document to publish at the ``client_id`` URL."""
        return dict(self._metadata)

    @property
    def jwks(self) -> t.Dict[str, t.List['Jwk']]:
        """JWK Set to publish at the ``jwks_uri`` of a confidential client."""
        return self._keyset.public_jwks

    def _authorize_flow(
        self,
        identifier: str,
        state: t.Optional[str],
        redirect_uri: t.Optional[str],
        scope: t.Optional[str],
        params: t.Mapping[str, t.Any],
    ) -> Flow[str]:
        redirect_uri = _flow.pick_redirect_uri(self._metadata, redirect_uri)
        scope = _flow.pick_scope(self._metadata, scope)

        resolved = yield from self._resolver._resolve_flow(identifier)
        server: AuthServerMetadata = resolved.server

        verifier, challenge = generate_pkce()
        dpop_jwk = generate_p256_jwk()
        auth_method = _flow.negotiate_auth_method(server, self._metadata, self._keyset)
        state_key = generate_nonce()
        form = _flow.build_par_form(
            redirect_uri, scope, state_key, challenge, identifier if resolved.identity else None, params
        )

        state_data = _flow.build_state_data(
            server, resolved, dpop_jwk, auth_method, verifier, redirect_uri, state, time.time()
        )
        yield call(self._state_store.set, state_key, state_data)

        try:
            body = yield from self._server_request_flow(
                server, server.pushed_authorization_request_endpoint, form, DpopKey(dpop_jwk), auth_method
            )

            return _flow.build_authorization_url(server, self.client_id, _flow.parse_par_response(body))
        except BaseException:
            # the request was never accepted, so nothing will come back for this state
            yield call(self._state_store.delete, state_key)
            raise

    def _callback_flow(self, params: t.Dict[str, str]) -> Flow[NewSession]:
        state_key = _flow.get_callback_state_key(params)

        stored = yield call(self._state_store.get, state_key)
        if stored is None:
            raise OAuthCallbackError('Unknown authorization request', params)

        # an authorization request is single-use
        yield call(self._state_store.delete, state_key)
        state = _flow.load_state_data(params, stored)

        try:
            return (yield from self._exchange_code_flow(params, state))
        except OAuthError as e:
            raise _flow.as_callback_error(e, params, state.app_state) from e

    def _exchange_code_flow(self, params: t.Mapping[str, str], state: OAuthStateData) -> Flow[NewSession]:
        server = yield from self._resolver._get_auth_server_metadata_flow(state.iss, False)
        code = _flow.check_callback(params, state, server, time.time(), self._state_ttl)
        _flow.ensure_auth_method(server, state.auth_method, self._keyset)

        key = DpopKey(state.dpop_jwk)
        requested_at = time.time()
        body = yield from self._server_request_flow(
            server,
            server.token_endpoint,
            _flow.build_code_form(code, state.pkce_verifier, state.redirect_uri),
            key,
            state.auth_method,
        )

        try:
            response = _flow.parse_token_response(body)
            _flow.check_expected_sub(state, response.sub)
            pds = yield from self._verify_issuer_flow(response.sub, server.issuer)
            if pds is None:
                raise OAuthError(f'Account {response.sub!r} is not served by the authorization server')
        except OAuthError:
            yield from self._revoke_issued_tokens_flow(server, key, state.auth_method, body)
            raise

        data = _flow.build_session_data(state.dpop_jwk, state.auth_method, response, server.issuer, pds, requested_at)

        return NewSession(data, server, key, state.app_state)

    def _adopt_session_flow(self, new: NewSession) -> Flow[None]:
        """Store a new session in place of the previous one of the account. Runs under the lock of the account."""
        try:
            # a previous session of the account would otherwise stay alive on the server
            with contextlib.suppress(OAuthError):
                yield from self._revoke_stored_session_flow(new.did)
        except BaseException:
            # the previous session could not be looked at, so it is left as it is
            yield from self._revoke_session_tokens_flow(new.data, new.server, new.key)
            raise

        yield from self._store_session_flow(new.did, new.data, new.server, new.key, False)

    def _revoke_session_tokens_flow(
        self, data: OAuthSessionData, server: AuthServerMetadata, key: DpopKey
    ) -> Flow[None]:
        token_set = data.token_set
        yield from self._revoke_token_flow(
            server, key, data.auth_method, token_set.refresh_token or token_set.access_token
        )

    def _revoke_stored_session_flow(self, did: str) -> Flow[None]:
        """Revoke and delete the stored session of an account. Runs under the lock of the account."""
        try:
            data = yield from self._load_session_flow(did)
        except TokenRefreshError:
            return

        if data is None:
            return

        try:
            server = yield from self._resolver._get_auth_server_metadata_flow(data.token_set.iss, False)
            yield from self._revoke_token_flow(
                server, DpopKey(data.dpop_jwk), data.auth_method, data.token_set.access_token
            )
        except OAuthError:
            # the session is forgotten even when the server could not be told
            pass

        yield from self._delete_session_flow(did, TokenRevokedError(did))

    def _drop_rejected_session_flow(self, did: str, rejected: TokenSet) -> Flow[None]:
        """Delete the session whose fresh tokens the resource server rejected. Runs under the lock of the account."""
        try:
            data = yield from self._load_session_flow(did)
        except TokenRefreshError:
            return

        # tokens someone else stored since are not the rejected ones
        if data is not None and data.token_set.access_token == rejected.access_token:
            yield from self._delete_session_flow(did, TokenInvalidError(did))

    def _read_session_flow(self, did: str) -> Flow[t.Optional[OAuthSessionData]]:
        stored = yield call(self._session_store.get, did)
        if stored is None:
            return None

        return _flow.load_session_data(did, stored)

    def _load_session_flow(self, did: str) -> Flow[t.Optional[OAuthSessionData]]:
        try:
            return (yield from self._read_session_flow(did))
        except TokenRefreshError as e:
            yield from self._delete_session_flow(did, e)
            raise

    def _store_session_flow(
        self, did: str, data: OAuthSessionData, server: AuthServerMetadata, key: DpopKey, replaces_stored: bool
    ) -> Flow[None]:
        """Store freshly issued tokens, or revoke them when they can not be stored.

        Args:
            did: DID of the account.
            data: Session with the new tokens.
            server: Authorization server that issued the tokens.
            key: Key of the session.
            replaces_stored: Whether the stored tokens were spent to get the new ones.
        """
        if data.token_set.sub != did:
            raise OAuthError('Session belongs to another account')

        try:
            yield call(self._session_store.set, did, data)
        except BaseException as e:
            yield from self._revoke_session_tokens_flow(data, server, key)
            if replaces_stored:
                with contextlib.suppress(Exception):
                    yield from self._delete_session_flow(did, e)

            raise

        if self._on_session_updated is not None:
            yield call(self._on_session_updated, did, data)

    def _delete_session_flow(self, did: str, cause: BaseException) -> Flow[None]:
        yield call(self._session_store.delete, did)
        if self._on_session_deleted is not None:
            yield call(self._on_session_deleted, did, cause)

    def _get_session_flow(
        self, did: str, refresh: 'RefreshMode', rejected: t.Optional[TokenSet]
    ) -> Flow[OAuthSessionData]:
        """Load the session of an account, refreshing its tokens when needed. Runs under the lock of the account."""
        data = yield from self._load_session_flow(did)
        if data is None:
            raise TokenRefreshError(did, 'No session is stored')

        if not _flow.needs_refresh(data.token_set, refresh, rejected, time.time(), random.random()):  # noqa: S311
            return data

        try:
            return (yield from self._refresh_session_flow(did, data))
        except (TokenRefreshError, AuthMethodUnsatisfiableError) as e:
            yield from self._delete_session_flow(did, e)
            raise

    def _refresh_session_flow(self, did: str, data: OAuthSessionData) -> Flow[OAuthSessionData]:
        """Get new tokens. The caller deletes the session when it can no longer be refreshed."""
        token_set = data.token_set
        if not token_set.refresh_token:
            raise TokenRefreshError(did, 'No refresh token available')

        server = yield from self._resolver._get_auth_server_metadata_flow(token_set.iss, False)
        _flow.ensure_auth_method(server, data.auth_method, self._keyset)

        # checked before the refresh token is spent, so that the new tokens are stored right after
        pds = yield from self._verify_issuer_flow(did, server.issuer)
        if pds is None:
            raise TokenRefreshError(did, 'The account is no longer served by the authorization server')

        key = DpopKey(data.dpop_jwk)
        requested_at = time.time()
        try:
            body = yield from self._server_request_flow(
                server, server.token_endpoint, _flow.build_refresh_form(token_set.refresh_token), key, data.auth_method
            )
        except OAuthResponseError as e:
            if not _flow.is_invalid_grant(e):
                raise

            return (yield from self._recover_from_invalid_grant_flow(did, data, e))

        try:
            response = _flow.parse_token_response(body)
            if response.sub != did:
                raise OAuthError('Refreshed tokens belong to another account')
        except OAuthError as e:
            yield from self._revoke_issued_tokens_flow(server, key, data.auth_method, body)
            raise TokenRefreshError(did, str(e)) from e

        refreshed = _flow.build_session_data(
            data.dpop_jwk, data.auth_method, response, server.issuer, pds, requested_at
        )
        yield from self._store_session_flow(did, refreshed, server, key, True)

        return refreshed

    def _recover_from_invalid_grant_flow(
        self, did: str, data: OAuthSessionData, error: OAuthResponseError
    ) -> Flow[OAuthSessionData]:
        if self._lock is None:
            # without a lock shared by every process, another one may have refreshed first
            yield Sleep(CONCURRENT_REFRESH_DELAY)

            current = yield from self._read_session_flow(did)
            if current is None:
                raise TokenRefreshError(did, 'The session was deleted by another process') from error

            if current.token_set != data.token_set:
                return current

        raise TokenRefreshError(did, error.error_description or 'The session was revoked') from error

    def _verify_issuer_flow(self, did: str, issuer: str) -> Flow[t.Optional[str]]:
        """Return the PDS of the account when the authorization server is the one that serves it."""
        resolved = yield from self._resolver._resolve_from_identity_flow(did, True)

        return _flow.get_verified_pds(resolved, issuer)

    def _revoke_issued_tokens_flow(
        self, server: AuthServerMetadata, key: DpopKey, auth_method: AuthMethod, body: _flow.Json
    ) -> Flow[None]:
        """Revoke the tokens of a token response the client does not accept."""
        token = body.get('refresh_token') or body.get('access_token')
        if isinstance(token, str):
            yield from self._revoke_token_flow(server, key, auth_method, token)

    def _revoke_token_flow(
        self, server: AuthServerMetadata, key: DpopKey, auth_method: AuthMethod, token: str
    ) -> Flow[None]:
        if not server.revocation_endpoint:
            return

        with contextlib.suppress(OAuthError):
            yield from self._send_server_request_flow(
                server, server.revocation_endpoint, _flow.build_revocation_form(token), key, auth_method
            )

    def _server_request_flow(
        self, server: AuthServerMetadata, url: str, form: _flow.Form, key: DpopKey, auth_method: AuthMethod
    ) -> Flow[_flow.Json]:
        response = yield from self._send_server_request_flow(server, url, form, key, auth_method)

        return _flow.parse_server_response(response)

    def _send_server_request_flow(
        self, server: AuthServerMetadata, url: str, form: _flow.Form, key: DpopKey, auth_method: AuthMethod
    ) -> Flow[HttpResponse]:
        origin = get_origin(url)

        for attempt in range(2):
            # the client assertion and the proof are single-use, so they are rebuilt for the retry
            credentials = _flow.build_client_credentials(
                auth_method, self.client_id, server.issuer, self._keyset, time.time()
            )
            request = _flow.build_server_request(url, form, credentials, key, self._nonces.get(origin))
            response: HttpResponse = yield call(self._http.request, 'POST', url, **request)
            self._nonces.update(origin, response.headers.get('dpop-nonce'))

            if attempt or not is_auth_server_nonce_error(response.status_code, response.json()):
                break

        return response
