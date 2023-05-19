from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict, Union

from atproto.xrpc_client.client.auth import get_jwt_payload

if TYPE_CHECKING:
    from atproto.xrpc_client import models


class SessionMethodsMixin:
    def _should_refresh_session(self) -> bool:
        expired_at = datetime.fromtimestamp(self._access_jwt_payload.exp, tz=timezone.utc)
        expired_at = expired_at - timedelta(minutes=15)  # let's update token a bit later than required

        datetime_now = datetime.now(timezone.utc)

        return datetime_now > expired_at

    def _set_session(
        self,
        session: Union[
            'models.ComAtprotoServerCreateSession.Response', 'models.ComAtprotoServerRefreshSession.Response'
        ],
    ) -> None:
        self._access_jwt = session.accessJwt
        self._access_jwt_payload = get_jwt_payload(session.accessJwt)

        self._refresh_jwt = session.refreshJwt
        self._refresh_jwt_payload = get_jwt_payload(session.refreshJwt)

        self._set_auth_headers(session.accessJwt)

    @staticmethod
    def _get_auth_headers(token: str) -> Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    def _set_auth_headers(self, token: str) -> None:
        self.request.set_additional_headers(self._get_auth_headers(token))  # noqa
