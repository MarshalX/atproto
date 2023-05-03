from datetime import datetime
from typing import Optional, Union

from xrpc_client import models
from xrpc_client.client.raw import ClientRaw


class Client(ClientRaw):
    """High-level client for XRPC of ATProtocol."""

    def __init__(self):
        super().__init__()
        self.me = None

    def login(self, login: str, password: str) -> models.GetProfileResponseRef:
        session = self.com.atproto.server.create_session(models.CreateSessionData(login, password))
        self.request.set_additional_headers({'Authorization': f'Bearer {session.accessJwt}'})

        self.me = self.bsky.actor.get_profile(models.GetProfileParams(session.handle))

        return self.me

    def send_post(
        self,
        text: str,
        profile_identify: Optional[str] = None,
        reply_to: Optional[Union[models.ReplyRef]] = None,
        embed: Optional[Union['models.Images', 'models.External', 'models.Record', 'models.RecordWithMedia']] = None,
    ) -> models.CreateRecordResponse:
        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        return self.com.atproto.repo.create_record(
            models.CreateRecordData(
                repo=repo,
                collection='app.bsky.feed.post',
                record=models.Post(createdAt=datetime.now().isoformat(), text=text, reply=reply_to, embed=embed),
            )
        )
