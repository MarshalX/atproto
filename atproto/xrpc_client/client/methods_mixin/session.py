import typing as t
from dataclasses import dataclass
from datetime import timedelta

import typing_extensions as te

from atproto.xrpc_client.client.auth import get_jwt_payload

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.client.auth import JwtPayload


@dataclass
class SessionString:
    access_jwt: str
    refresh_jwt: str
    did: str
    handle: str

    _SESSION_STRING_SEPARATOR: te.Final[te.Literal[':::']] = ':::'

    def encode(self) -> str:
        payload = [
            self.handle,
            self.did,
            self.access_jwt,
            self.refresh_jwt,
        ]
        return self._SESSION_STRING_SEPARATOR.join(payload)

    @classmethod
    def decode(cls, string: str) -> 'SessionString':
        handle, did, access_jwt, refresh_jwt = string.split(cls._SESSION_STRING_SEPARATOR)
        return cls(access_jwt, refresh_jwt, did, handle)


SessionResponse: te.TypeAlias = t.Union[
    'models.ComAtprotoServerCreateSession.Response',
    'models.ComAtprotoServerRefreshSession.Response',
    'SessionString',
]


class SessionMethodsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._access_jwt: t.Optional[str] = None
        self._access_jwt_payload: t.Optional['JwtPayload'] = None

        self._refresh_jwt: t.Optional[str] = None
        self._refresh_jwt_payload: t.Optional['JwtPayload'] = None

        self._session: t.Optional[SessionString] = None

    def _should_refresh_session(self) -> bool:
        expired_at = self.get_time_from_timestamp(self._access_jwt_payload.exp)
        expired_at = expired_at - timedelta(minutes=15)  # let's update the token a bit later than required

        return self.get_current_time() > expired_at

    def _set_session(self, session: SessionResponse) -> None:
        self._access_jwt = session.access_jwt
        self._access_jwt_payload = get_jwt_payload(session.access_jwt)

        self._refresh_jwt = session.refresh_jwt
        self._refresh_jwt_payload = get_jwt_payload(session.refresh_jwt)

        self._session = SessionString(
            access_jwt=session.access_jwt,
            refresh_jwt=session.refresh_jwt,
            did=session.did,
            handle=session.handle,
        )

        self._set_auth_headers(session.access_jwt)

    @staticmethod
    def _get_auth_headers(token: str) -> t.Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _set_auth_headers(self, token: str) -> None:
        self.request.set_additional_headers(self._get_auth_headers(token))

    def _import_session_string(self, string: str) -> SessionString:
        session = SessionString.decode(string)
        self._set_session(session)
        return session

    def export_session_string(self) -> str:
        """Export session string.

        Note:
            This method is useful for storing the session and reusing it later.

        Warning:
            You should use it if you create the client instance often.
            Because of server rate limits for `createSession`.
            Rate limited by handle.
            30/5 min, 300/day.

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
        return self._session.encode()
