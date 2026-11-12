import typing as t

import httpx
import typing_extensions as te

from atproto_oauth._effects import Call, call, perform, perform_async
from atproto_oauth.dpop import (
    DpopKey,
    build_dpop_proof,
    is_invalid_token_error,
    is_resource_server_nonce_error,
)
from atproto_oauth.exceptions import OAuthError
from atproto_oauth.models import OAuthSessionData, TokenInfo, TokenSet
from atproto_oauth.scopes import ScopePermissionsTransition
from atproto_oauth.security import get_origin

if t.TYPE_CHECKING:
    from atproto_oauth._flow import RefreshMode
    from atproto_oauth.async_client import AsyncOAuthClient
    from atproto_oauth.client import OAuthClient

_Step = t.Union[httpx.Request, Call]
_Policy = t.Generator[_Step, t.Any, None]


class _DpopAuth(httpx.Auth):
    def __init__(self, session: '_SessionBase') -> None:
        self._session = session

    def _send(self, request: httpx.Request, token_set: TokenSet) -> t.Generator[_Step, t.Any, t.Optional[TokenSet]]:
        """Send the request, repeating it once when the server asks for a new nonce.

        Returns:
            The tokens the request was sent with when the server rejected them, :obj:`None` otherwise.
        """
        session = self._session
        nonces = session._client._nonces
        url = str(request.url)
        origin = get_origin(url)

        for attempt in range(2):
            request.headers['Authorization'] = f'DPoP {token_set.access_token}'
            request.headers['DPoP'] = build_dpop_proof(
                session._key, request.method, url, nonces.get(origin), token_set.access_token
            )

            response: httpx.Response = yield request
            nonces.update(origin, response.headers.get('dpop-nonce'))

            www_authenticate = response.headers.get('www-authenticate')
            if attempt or not is_resource_server_nonce_error(response.status_code, www_authenticate):
                break

        if is_invalid_token_error(response.status_code, www_authenticate):
            return token_set

        return None

    def _authenticate(self, request: httpx.Request) -> _Policy:
        """Decide what to send. Yields requests to send and calls to make, and is sent back their results."""
        session = self._session

        # tokens are only ever sent to the PDS of the account, and never over an explicit authorization
        if 'Authorization' in request.headers or get_origin(str(request.url)) != get_origin(session.pds_endpoint):
            yield request
            return

        token_set = yield from self._load_token_set('auto', None)
        rejected = yield from self._send(request, token_set)
        if rejected is None:
            return

        try:
            token_set = yield from self._load_token_set(True, rejected)
        except OAuthError:
            return

        rejected = yield from self._send(request, token_set)
        if rejected is not None:
            yield call(session._client._drop_rejected_session, session.did, rejected)

    def _load_token_set(
        self, refresh: 'RefreshMode', rejected: t.Optional[TokenSet]
    ) -> t.Generator[_Step, t.Any, TokenSet]:
        session = self._session
        data: OAuthSessionData = yield call(session._client._get_session, session.did, refresh, rejected)
        session._set_data(data)

        return data.token_set

    @te.override
    def sync_auth_flow(self, request: httpx.Request) -> t.Generator[httpx.Request, httpx.Response, None]:
        if self._session._is_async:
            raise RuntimeError('AsyncOAuthSession can only be used with AsyncClient; use OAuthSession with Client')

        # a streamed body can not be sent twice
        request.read()

        policy = self._authenticate(request)
        try:
            step = next(policy)
            while True:
                if isinstance(step, httpx.Request):
                    step = policy.send((yield step))
                    continue

                try:
                    result = perform(step)
                except BaseException as e:  # noqa: BLE001
                    step = policy.throw(e)
                else:
                    step = policy.send(result)
        except StopIteration:
            return

    @te.override
    async def async_auth_flow(self, request: httpx.Request) -> t.AsyncGenerator[httpx.Request, httpx.Response]:
        if not self._session._is_async:
            raise RuntimeError('OAuthSession can only be used with Client; use AsyncOAuthSession with AsyncClient')

        # a streamed body can not be sent twice
        await request.aread()

        policy = self._authenticate(request)
        try:
            step = next(policy)
            while True:
                if isinstance(step, httpx.Request):
                    step = policy.send((yield step))
                    continue

                try:
                    result = await perform_async(step)
                except BaseException as e:  # noqa: BLE001
                    step = policy.throw(e)
                else:
                    step = policy.send(result)
        except StopIteration:
            return


class _SessionBase:
    _is_async: t.ClassVar[bool]

    def __init__(self, client: t.Any, data: OAuthSessionData) -> None:
        self._client = client
        self._data = data
        self._key = DpopKey(data.dpop_jwk)
        self._auth = _DpopAuth(self)

    def _set_data(self, data: OAuthSessionData) -> None:
        # a new login of the account replaces the key along with the tokens
        if data.dpop_jwk != self._data.dpop_jwk:
            self._key = DpopKey(data.dpop_jwk)

        self._data = data

    @property
    def did(self) -> str:
        """DID of the account."""
        return self._data.token_set.sub

    @property
    def pds_endpoint(self) -> str:
        """URL of the account's PDS, as of the last time the tokens were loaded."""
        return self._data.token_set.aud

    @property
    def permissions(self) -> ScopePermissionsTransition:
        """Permissions the granted scope gives, as of the last time the tokens were loaded."""
        return ScopePermissionsTransition(self._data.token_set.scope)

    @property
    def httpx_auth(self) -> httpx.Auth:
        """Authentication that signs requests to the PDS and keeps the tokens fresh."""
        return self._auth

    def __repr__(self) -> str:
        return f'<{type(self).__name__} did={self.did}>'


class OAuthSession(_SessionBase):
    """Session of an account. Pass it to :py:meth:`atproto_client.Client.login_oauth`.

    Sessions are created by :py:meth:`~atproto_oauth.OAuthClient.callback` and
    :py:meth:`~atproto_oauth.OAuthClient.restore`.
    """

    _is_async = False

    def __init__(self, client: 'OAuthClient', data: OAuthSessionData) -> None:
        super().__init__(client, data)

    def get_token_info(self, refresh: 'RefreshMode' = 'auto') -> TokenInfo:
        """Describe the tokens of the session.

        Args:
            refresh: ``'auto'`` refreshes the tokens when they are about to expire,
                :obj:`True` always refreshes them, :obj:`False` never does.

        Returns:
            :obj:`TokenInfo`: Description of the tokens, without the tokens.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthError`: The session is gone or could not be refreshed.
        """
        self._set_data(self._client._get_session(self.did, refresh))

        return TokenInfo.from_token_set(self._data.token_set)

    def sign_out(self) -> None:
        """Revoke the session and delete it from the session store."""
        self._client.revoke(self.did)


class AsyncOAuthSession(_SessionBase):
    """Session of an account. Pass it to :py:meth:`atproto_client.AsyncClient.login_oauth`.

    Sessions are created by :py:meth:`~atproto_oauth.AsyncOAuthClient.callback` and
    :py:meth:`~atproto_oauth.AsyncOAuthClient.restore`.
    """

    _is_async = True

    def __init__(self, client: 'AsyncOAuthClient', data: OAuthSessionData) -> None:
        super().__init__(client, data)

    async def get_token_info(self, refresh: 'RefreshMode' = 'auto') -> TokenInfo:
        """Describe the tokens of the session.

        Args:
            refresh: ``'auto'`` refreshes the tokens when they are about to expire,
                :obj:`True` always refreshes them, :obj:`False` never does.

        Returns:
            :obj:`TokenInfo`: Description of the tokens, without the tokens.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthError`: The session is gone or could not be refreshed.
        """
        self._set_data(await self._client._get_session(self.did, refresh))

        return TokenInfo.from_token_set(self._data.token_set)

    async def sign_out(self) -> None:
        """Revoke the session and delete it from the session store."""
        await self._client.revoke(self.did)
