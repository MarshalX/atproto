import contextlib
import threading
import typing as t

from atproto_oauth._base import (
    DEFAULT_MAX_PENDING_AUTHORIZATIONS,
    DEFAULT_STATE_TTL,
    KeyedLocks,
    OAuthCallbackResult,
    _OAuthClientBase,
)
from atproto_oauth._effects import run_flow
from atproto_oauth.resolver import OAuthResolver
from atproto_oauth.security import DEFAULT_TIMEOUT, HttpClient
from atproto_oauth.session import OAuthSession
from atproto_oauth.stores import MemoryStore, SessionStore, StateStore

if t.TYPE_CHECKING:
    import httpx
    from atproto_identity.resolver import IdResolver

    from atproto_oauth._flow import RefreshMode
    from atproto_oauth.models import OAuthSessionData, TokenSet

LockFactory = t.Callable[[str], t.ContextManager[t.Any]]
SessionUpdatedCallback = t.Callable[[str, 'OAuthSessionData'], None]
SessionDeletedCallback = t.Callable[[str, BaseException], None]


class OAuthClient(_OAuthClientBase):
    """OAuth client of the AT Protocol.

    Use :py:meth:`loopback`, :py:meth:`public` or :py:meth:`confidential` to create one
    without writing the client metadata by hand.

    Args:
        client_metadata: Client metadata document.
        keys: Client authentication keys of a confidential client, as private P-256 JWKs with a ``kid``.
        state_store: Storage of authorization requests in progress. In memory by default.
        session_store: Storage of sessions. In memory by default, which loses them on restart.
        id_resolver: Identity resolver.
        transport: ``httpx`` transport for requests to the PDS and the authorization server.
        allow_http: Accept ``http`` URLs and loopback hosts. For development environments.
        lock: Returns a context manager that is exclusive for a DID across processes.
            Without it, concurrent token refreshes are only prevented within this client.
        on_session_updated: Called with the DID and the session data after a session is stored.
            Runs under the lock of the account, so it must not call this client for the same account.
            An exception it raises propagates; the session stays stored.
        on_session_deleted: Called with the DID and the cause after a session is deleted.
            Runs under the lock of the account as well.
        state_ttl: Seconds an authorization request may take.
        timeout: Timeout of requests to the PDS and the authorization server, in seconds.
    """

    def __init__(
        self,
        client_metadata: t.Mapping[str, t.Any],
        *,
        keys: t.Optional[t.Iterable[t.Mapping[str, t.Any]]] = None,
        state_store: t.Optional[StateStore] = None,
        session_store: t.Optional[SessionStore] = None,
        id_resolver: t.Optional['IdResolver'] = None,
        transport: t.Optional['httpx.BaseTransport'] = None,
        allow_http: bool = False,
        lock: t.Optional[LockFactory] = None,
        on_session_updated: t.Optional[SessionUpdatedCallback] = None,
        on_session_deleted: t.Optional[SessionDeletedCallback] = None,
        state_ttl: float = DEFAULT_STATE_TTL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if id_resolver is None:
            from atproto_identity.resolver import IdResolver

            id_resolver = IdResolver()

        if state_store is None:
            state_store = MemoryStore(ttl=state_ttl, max_size=DEFAULT_MAX_PENDING_AUTHORIZATIONS)

        http = HttpClient(transport, allow_http, timeout)
        super().__init__(
            client_metadata,
            keys,
            state_store,
            session_store if session_store is not None else MemoryStore(),
            OAuthResolver(id_resolver, http, allow_http),
            http,
            lock,
            on_session_updated,
            on_session_deleted,
            state_ttl,
        )
        self._locks: KeyedLocks[threading.Lock] = KeyedLocks(threading.Lock)

    @property
    def resolver(self) -> OAuthResolver:
        """Resolver of authorization servers."""
        resolver: OAuthResolver = self._resolver
        return resolver

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def authorize(
        self,
        identifier: str,
        *,
        state: t.Optional[str] = None,
        redirect_uri: t.Optional[str] = None,
        scope: t.Optional[str] = None,
        **params: t.Any,
    ) -> str:
        """Start an authorization and return the URL to send the user to.

        Args:
            identifier: Handle or DID of the account, or the URL of a PDS or an entryway.
            state: Application state to get back from :py:meth:`callback`.
                A web application must bind it to the browser session, see the OAuth guide.
            redirect_uri: One of the registered redirect URIs. The first one by default.
            scope: Subset of the registered scope. The whole registered scope by default.
            **params: More authorization request parameters, such as ``prompt``.

        Returns:
            :obj:`str`: Authorization URL.

        Raises:
            :class:`ValueError`: The redirect URI, the scope or an extra parameter is not allowed.
            :class:`atproto_oauth.exceptions.OAuthError`: The authorization could not be started.
        """
        return run_flow(self._authorize_flow(identifier, state, redirect_uri, scope, params))

    def callback(self, params: t.Mapping[str, str]) -> OAuthCallbackResult[OAuthSession]:
        """Complete an authorization with the query parameters the user was redirected back with.

        Args:
            params: Query parameters of the redirect URI.

        Returns:
            :obj:`OAuthCallbackResult`: The session and the application state.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthCallbackError`: The authorization failed.
        """
        new = run_flow(self._callback_flow(dict(params)))
        with self._session_lock(new.did):
            run_flow(self._adopt_session_flow(new))

        return OAuthCallbackResult(OAuthSession(self, new.data), new.app_state)

    def restore(self, did: str, refresh: 'RefreshMode' = 'auto') -> OAuthSession:
        """Load the stored session of an account.

        Args:
            did: DID of the account.
            refresh: ``'auto'`` refreshes the tokens when they are about to expire,
                :obj:`True` always refreshes them, :obj:`False` never does.

        Returns:
            :obj:`OAuthSession`: Session of the account.

        Raises:
            :class:`atproto_oauth.exceptions.TokenRefreshError`: There is no usable session.
            :class:`atproto_oauth.exceptions.AuthMethodUnsatisfiableError`: The client authentication key
                of the session is gone. The session is deleted.
            :class:`atproto_oauth.exceptions.OAuthError`: The tokens could not be refreshed for now.
        """
        return OAuthSession(self, self._get_session(did, refresh))

    def revoke(self, did: str) -> None:
        """Revoke the session of an account and delete it from the session store.

        Does nothing when there is no session.

        Args:
            did: DID of the account.
        """
        with self._session_lock(did):
            run_flow(self._revoke_stored_session_flow(did))

    def _get_session(
        self, did: str, refresh: 'RefreshMode' = 'auto', rejected: t.Optional['TokenSet'] = None
    ) -> 'OAuthSessionData':
        with self._session_lock(did):
            return run_flow(self._get_session_flow(did, refresh, rejected))

    def _drop_rejected_session(self, did: str, rejected: 'TokenSet') -> None:
        with self._session_lock(did):
            run_flow(self._drop_rejected_session_flow(did, rejected))

    @contextlib.contextmanager
    def _session_lock(self, did: str) -> t.Generator[None, None, None]:
        lock = self._locks.enter(did)
        try:
            with lock:
                if self._lock is None:
                    yield
                else:
                    with self._lock(did):
                        yield
        finally:
            self._locks.leave(did)
