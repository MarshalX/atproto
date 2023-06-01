import typing as t
from datetime import datetime, timedelta, timezone

from atproto.xrpc_client.client.auth import get_jwt_payload

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.client.auth import JwtPayload


class SessionMethodsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._access_jwt: t.Optional[str] = None
        self._access_jwt_payload: t.Optional['JwtPayload'] = None

        self._refresh_jwt: t.Optional[str] = None
        self._refresh_jwt_payload: t.Optional['JwtPayload'] = None

    def _should_refresh_session(self) -> bool:
        expired_at = datetime.fromtimestamp(self._access_jwt_payload.exp, tz=timezone.utc)
        expired_at = expired_at - timedelta(minutes=15)  # let's update the token a bit later than required

        datetime_now = datetime.now(timezone.utc)

        return datetime_now > expired_at

    def _set_session(
        self,
        session: t.Union[
            'models.ComAtprotoServerCreateSession.Response', 'models.ComAtprotoServerRefreshSession.Response'
        ],
    ) -> None:
        self._access_jwt = session.accessJwt
        self._access_jwt_payload = get_jwt_payload(session.accessJwt)

        self._refresh_jwt = session.refreshJwt
        self._refresh_jwt_payload = get_jwt_payload(session.refreshJwt)

        self._set_auth_headers(session.accessJwt)

    @staticmethod
    def _get_auth_headers(token: str) -> t.Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _set_auth_headers(self, token: str) -> None:
        self.request.set_additional_headers(self._get_auth_headers(token))
