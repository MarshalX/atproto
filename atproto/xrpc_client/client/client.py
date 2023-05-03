from xrpc_client import models
from xrpc_client.client.raw import ClientRaw


class Client(ClientRaw):
    """High-level client for XRPC of ATProtocol."""

    def login(self, login: str, password: str) -> models.GetProfileResponseRef:
        session = self.com.atproto.server.create_session(models.CreateSessionData(login, password))
        self.request.set_additional_headers({'Authorization': f'Bearer {session.accessJwt}'})
        return self.bsky.actor.get_profile(models.GetProfileParams(session.handle))
