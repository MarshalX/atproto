import asyncio
import typing as t
from datetime import timedelta

from atproto_server.auth.jwt import get_jwt_payload

from atproto_client.client.methods_mixin.time import TimeMethodsMixin
from atproto_client.client.session import (
    AsyncSessionChangeCallback,
    Session,
    SessionChangeCallback,
    SessionEvent,
    SessionResponse,
)
from atproto_client.exceptions import LoginRequiredError

if t.TYPE_CHECKING:
    from atproto_server.auth.jwt import JwtPayload


class SessionDispatchMixin:
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._on_session_change_callbacks: t.List[SessionChangeCallback] = []
        self._on_session_change_async_callbacks: t.List[AsyncSessionChangeCallback] = []

    def on_session_change(self, callback: SessionChangeCallback) -> None:
        """Register a callback for session change event.

        Args:
            callback: A callback to be called when the session changes.
                The callback must accept two arguments: event and session.

        Example:
            >>> from atproto import Client, SessionEvent, Session
            >>>
            >>> client = Client()
            >>>
            >>> def on_session_change(event: SessionEvent, session: Session):
            >>>     print(event, session)
            >>>
            >>> client.on_session_change(on_session_change)

        Returns:
            :obj:`None`
        """
        self._on_session_change_callbacks.append(callback)

    def _call_on_session_change_callbacks(self, event: SessionEvent, session: Session) -> None:
        for on_session_change_callback in self._on_session_change_callbacks:
            on_session_change_callback(event, session)


class AsyncSessionDispatchMixin:
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._on_session_change_async_callbacks: t.List[AsyncSessionChangeCallback] = []

    def on_session_change(self, callback: AsyncSessionChangeCallback) -> None:
        """Register a callback for session change event.

        Args:
            callback: A callback to be called when the session changes.
                The callback must accept two arguments: event and session.

        Note:
            Possible events: `SessionEvent.IMPORT`, `SessionEvent.CREATE`, `SessionEvent.REFRESH`.

        Tip:
            You should save the session string to persistent storage
            on `SessionEvent.CREATE` and `SessionEvent.REFRESN` event.

        Example:
            >>> from atproto import AsyncClient, SessionEvent, Session
            >>>
            >>> client = AsyncClient()
            >>>
            >>> async def on_session_change(event: SessionEvent, session: Session):
            >>>     print(event, session)
            >>>
            >>> client.on_session_change(on_session_change)

        Returns:
            :obj:`None`
        """
        self._on_session_change_async_callbacks.append(callback)

    async def _call_on_session_change_callbacks(self, event: SessionEvent, session: Session) -> None:
        coroutines: t.List[t.Coroutine[t.Any, t.Any, None]] = []
        for on_session_change_async_callback in self._on_session_change_async_callbacks:
            coroutines.append(on_session_change_async_callback(event, session))

        await asyncio.gather(*coroutines)


class SessionMethodsMixin(TimeMethodsMixin):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._access_jwt: t.Optional[str] = None
        self._access_jwt_payload: t.Optional['JwtPayload'] = None

        self._refresh_jwt: t.Optional[str] = None
        self._refresh_jwt_payload: t.Optional['JwtPayload'] = None

        self._session: t.Optional[Session] = None

    def _should_refresh_session(self) -> bool:
        if not self._access_jwt_payload or not self._access_jwt_payload.exp:
            raise LoginRequiredError

        expired_at = self.get_time_from_timestamp(self._access_jwt_payload.exp)
        expired_at = expired_at - timedelta(minutes=15)  # let's update the token a bit earlier than required

        return self.get_current_time() > expired_at

    def _set_session_common(self, session: SessionResponse) -> Session:
        self._access_jwt = session.access_jwt
        self._access_jwt_payload = get_jwt_payload(session.access_jwt)

        self._refresh_jwt = session.refresh_jwt
        self._refresh_jwt_payload = get_jwt_payload(session.refresh_jwt)

        self._session = Session(
            access_jwt=session.access_jwt,
            refresh_jwt=session.refresh_jwt,
            did=session.did,
            handle=session.handle,
        )

        self._set_auth_headers(session.access_jwt)

        return self._session

    @staticmethod
    def _get_auth_headers(token: str) -> t.Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _set_auth_headers(self, token: str) -> None:
        self.request.set_additional_headers(self._get_auth_headers(token))

    def export_session_string(self) -> str:
        """Export session string.

        Note:
            This method is useful for storing the session and reusing it later.

        Warning:
            You should use it if you create the client instance often.
            Because of server rate limits for `createSession`.
            Rate limited by handle.
            30/5 min, 300/day.

        Attention:
            You must export session at the end of the Client`s life cycle!
            Alternatively, you can subscribe to the session change event.
            Use :py:attr:`~on_session_change` to register handler.

        Example:
            >>> from atproto import Client
            >>> # the first time login with login and password
            >>> client = Client()
            >>> client.login('login', 'password')
            >>> session_string = client.export_session_string()
            >>> # store session_string somewhere.
            >>> # for example, in env and next time use it for login
            >>> client2 = Client()
            >>> client2.login(session_string=session_string)

        Returns:
            :obj:`str`: Session string.
        """
        if not self._session:
            raise LoginRequiredError

        return self._session.export()
