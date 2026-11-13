import asyncio
import contextlib
import typing as t
import webbrowser

import typing_extensions as te

from atproto_oauth._base import (
    DEFAULT_MAX_PENDING_AUTHORIZATIONS,
    DEFAULT_STATE_TTL,
    KeyedLocks,
    OAuthCallbackResult,
    _OAuthClientBase,
)
from atproto_oauth._effects import run_flow_async
from atproto_oauth.loopback import DEFAULT_LOGIN_TIMEOUT, login_flow
from atproto_oauth.metadata import ATPROTO_SCOPE
from atproto_oauth.resolver import AsyncOAuthResolver
from atproto_oauth.security import DEFAULT_TIMEOUT, AsyncHttpClient
from atproto_oauth.session import AsyncOAuthSession
from atproto_oauth.stores import AsyncSessionStore, AsyncStateStore, MemoryStore, SessionStore, StateStore

if t.TYPE_CHECKING:
    import httpx
    from atproto_identity.resolver import AsyncIdResolver

    from atproto_oauth._flow import RefreshMode
    from atproto_oauth.models import OAuthSessionData, TokenSet

AsyncLockFactory = t.Callable[[str], t.AsyncContextManager[t.Any]]
AsyncSessionUpdatedCallback = t.Callable[[str, 'OAuthSessionData'], t.Optional[t.Awaitable[None]]]
AsyncSessionDeletedCallback = t.Callable[[str, BaseException], t.Optional[t.Awaitable[None]]]


class _AsyncClientOptions(te.TypedDict, total=False):
    """Arguments the client takes besides its metadata and keys."""

    state_store: t.Union[AsyncStateStore, StateStore]
    session_store: t.Union[AsyncSessionStore, SessionStore]
    id_resolver: 'AsyncIdResolver'
    transport: 'httpx.AsyncBaseTransport'
    allow_http: bool
    lock: AsyncLockFactory
    on_session_updated: AsyncSessionUpdatedCallback
    on_session_deleted: AsyncSessionDeletedCallback
    state_ttl: float
    timeout: float


class AsyncOAuthClient(_OAuthClientBase):
    """OAuth client of the AT Protocol.

    Use :py:meth:`loopback`, :py:meth:`public` or :py:meth:`confidential` to create one
    without writing the client metadata by hand.

    Args:
        client_metadata: Client metadata document.
        keys: Client authentication keys of a confidential client, as private P-256 JWKs with a ``kid``.
        state_store: Storage of authorization requests in progress, synchronous or asynchronous.
            In memory by default.
        session_store: Storage of sessions, synchronous or asynchronous.
            In memory by default, which loses them on restart.
        id_resolver: Identity resolver.
        transport: ``httpx`` transport for requests to the PDS and the authorization server.
        allow_http: Accept ``http`` URLs and loopback hosts. For development environments.
        lock: Returns an asynchronous context manager that is exclusive for a DID across processes.
            Without it, concurrent token refreshes are only prevented within this client.
        on_session_updated: Called with the DID and the session data after a session is stored.
            Runs under the lock of the account, so it must not call this client for the same account.
            An exception it raises propagates; the session stays stored.
            May be a coroutine function.
        on_session_deleted: Called with the DID and the cause after a session is deleted.
            May be a coroutine function.
            Runs under the lock of the account as well.
        state_ttl: Seconds an authorization request may take.
        timeout: Timeout of requests to the PDS and the authorization server, in seconds.
    """

    @classmethod
    @te.override
    def loopback(
        cls,
        redirect_uri: t.Optional[t.Union[str, t.Sequence[str]]] = None,
        scope: str = ATPROTO_SCOPE,
        **kwargs: te.Unpack[_AsyncClientOptions],
    ) -> te.Self:
        return super().loopback(redirect_uri, scope, **kwargs)

    @classmethod
    @te.override
    def public(
        cls,
        client_id: str,
        redirect_uri: t.Union[str, t.Sequence[str]],
        scope: str,
        metadata: t.Optional[t.Mapping[str, t.Any]] = None,
        **kwargs: te.Unpack[_AsyncClientOptions],
    ) -> te.Self:
        return super().public(client_id, redirect_uri, scope, metadata, **kwargs)

    @classmethod
    @te.override
    def confidential(
        cls,
        client_id: str,
        redirect_uri: t.Union[str, t.Sequence[str]],
        scope: str,
        keys: t.Iterable[t.Mapping[str, t.Any]],
        metadata: t.Optional[t.Mapping[str, t.Any]] = None,
        **kwargs: te.Unpack[_AsyncClientOptions],
    ) -> te.Self:
        return super().confidential(client_id, redirect_uri, scope, keys, metadata, **kwargs)

    def __init__(
        self,
        client_metadata: t.Mapping[str, t.Any],
        *,
        keys: t.Optional[t.Iterable[t.Mapping[str, t.Any]]] = None,
        state_store: t.Optional[t.Union[AsyncStateStore, StateStore]] = None,
        session_store: t.Optional[t.Union[AsyncSessionStore, SessionStore]] = None,
        id_resolver: t.Optional['AsyncIdResolver'] = None,
        transport: t.Optional['httpx.AsyncBaseTransport'] = None,
        allow_http: bool = False,
        lock: t.Optional[AsyncLockFactory] = None,
        on_session_updated: t.Optional[AsyncSessionUpdatedCallback] = None,
        on_session_deleted: t.Optional[AsyncSessionDeletedCallback] = None,
        state_ttl: float = DEFAULT_STATE_TTL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if id_resolver is None:
            from atproto_identity.resolver import AsyncIdResolver

            id_resolver = AsyncIdResolver()

        if state_store is None:
            state_store = MemoryStore(ttl=state_ttl, max_size=DEFAULT_MAX_PENDING_AUTHORIZATIONS)

        http = AsyncHttpClient(transport, allow_http, timeout)
        super().__init__(
            client_metadata,
            keys,
            state_store,
            session_store if session_store is not None else MemoryStore(),
            AsyncOAuthResolver(id_resolver, http, allow_http),
            http,
            lock,
            on_session_updated,
            on_session_deleted,
            state_ttl,
        )
        self._locks: KeyedLocks[asyncio.Lock] = KeyedLocks(asyncio.Lock)

    @property
    def resolver(self) -> AsyncOAuthResolver:
        """Resolver of authorization servers."""
        resolver: AsyncOAuthResolver = self._resolver
        return resolver

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()

    async def authorize(
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
        return await run_flow_async(self._authorize_flow(identifier, state, redirect_uri, scope, params))

    async def callback(self, params: t.Mapping[str, str]) -> OAuthCallbackResult[AsyncOAuthSession]:
        """Complete an authorization with the query parameters the user was redirected back with.

        Args:
            params: Query parameters of the redirect URI.

        Returns:
            :obj:`OAuthCallbackResult`: The session and the application state.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthCallbackError`: The authorization failed.
        """
        new = await run_flow_async(self._callback_flow(dict(params)))
        async with self._session_lock(new.did):
            await run_flow_async(self._adopt_session_flow(new))

        return OAuthCallbackResult(AsyncOAuthSession(self, new.data), new.app_state)

    async def login_with_browser(
        self,
        identifier: str,
        *,
        open_url: t.Optional[t.Callable[[str], t.Any]] = None,
        timeout: t.Optional[float] = DEFAULT_LOGIN_TIMEOUT,
        **params: t.Any,
    ) -> AsyncOAuthSession:
        """Authorize an account in the browser of this machine and return its session.

        Runs a local HTTP server for the redirect back, so the client needs a redirect URI
        on ``127.0.0.1`` or ``[::1]``, as a client made by :py:meth:`loopback` has.

        Args:
            identifier: Handle or DID of the account, or the URL of a PDS or an entryway.
            open_url: Called with the authorization URL. Opens the default browser by default.
            timeout: Seconds to wait for the user. :obj:`None` waits forever.
            **params: Other arguments of :py:meth:`authorize`, such as ``scope``.

        Returns:
            :obj:`AsyncOAuthSession`: Session of the account.

        Raises:
            :class:`ValueError`: The client has no loopback redirect URI.
            :class:`atproto_oauth.exceptions.OAuthCallbackError`: The authorization failed
                or was not completed in time.
        """
        flow = login_flow(self, identifier, open_url or webbrowser.open, timeout, params)
        session: AsyncOAuthSession = await run_flow_async(flow)
        return session

    async def restore(self, identifier: str, refresh: 'RefreshMode' = 'auto') -> AsyncOAuthSession:
        """Load the stored session of an account.

        Args:
            identifier: DID or handle of the account. A handle is resolved over the network first.
                A web service must pass the DID it stored at login, not a handle typed by a visitor.
            refresh: ``'auto'`` refreshes the tokens when they are about to expire,
                :obj:`True` always refreshes them, :obj:`False` never does.

        Returns:
            :obj:`AsyncOAuthSession`: Session of the account.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthResolverError`: The handle could not be resolved.
            :class:`atproto_oauth.exceptions.TokenRefreshError`: There is no usable session.
            :class:`atproto_oauth.exceptions.AuthMethodUnsatisfiableError`: The client authentication key
                of the session is gone. The session is deleted.
            :class:`atproto_oauth.exceptions.OAuthError`: The tokens could not be refreshed for now.
        """
        did = await run_flow_async(self._resolve_did_flow(identifier))

        return AsyncOAuthSession(self, await self._get_session(did, refresh))

    async def revoke(self, did: str) -> None:
        """Revoke the session of an account and delete it from the session store.

        Does nothing when there is no session.

        Args:
            did: DID of the account.
        """
        async with self._session_lock(did):
            await run_flow_async(self._revoke_stored_session_flow(did))

    async def _get_session(
        self, did: str, refresh: 'RefreshMode' = 'auto', rejected: t.Optional['TokenSet'] = None
    ) -> 'OAuthSessionData':
        async with self._session_lock(did):
            return await run_flow_async(self._get_session_flow(did, refresh, rejected))

    async def _drop_rejected_session(self, did: str, rejected: 'TokenSet') -> None:
        async with self._session_lock(did):
            await run_flow_async(self._drop_rejected_session_flow(did, rejected))

    @contextlib.asynccontextmanager
    async def _session_lock(self, did: str) -> t.AsyncGenerator[None, None]:
        lock = self._locks.enter(did)
        try:
            async with lock:
                if self._lock is None:
                    yield
                else:
                    async with self._lock(did):
                        yield
        finally:
            self._locks.leave(did)
