import typing as t
from datetime import timedelta

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
        expired_at = self.get_time_from_timestamp(self._access_jwt_payload.exp)
        expired_at = expired_at - timedelta(minutes=15)  # let's update the token a bit later than required

        return self.get_current_time() > expired_at

    def _set_session(
        self,
        session: t.Union[
            'models.ComAtprotoServerCreateSession.Response', 'models.ComAtprotoServerRefreshSession.Response'
        ],
    ) -> None:
        self._access_jwt = session.access_jwt
        self._access_jwt_payload = get_jwt_payload(session.access_jwt)

        self._refresh_jwt = session.refresh_jwt
        self._refresh_jwt_payload = get_jwt_payload(session.refresh_jwt)

        self._set_auth_headers(session.access_jwt)

    @staticmethod
    def _get_auth_headers(token: str) -> t.Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _set_auth_headers(self, token: str) -> None:
        self.request.set_additional_headers(self._get_auth_headers(token))
