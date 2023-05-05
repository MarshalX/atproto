###########################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS #
###########################################################

from datetime import datetime
from typing import Optional, Union

from xrpc_client import models
from xrpc_client.client.raw import AsyncClientRaw


class AsyncClient(AsyncClientRaw):
    """High-level client for XRPC of ATProto."""

    def __init__(self):
        super().__init__()
        self.me = None

    async def login(self, login: str, password: str) -> models.AppBskyActorGetProfile.ResponseRef:
        session = await self.com.atproto.server.create_session(
            models.ComAtprotoServerCreateSession.Data(login, password)
        )
        self.request.set_additional_headers({'Authorization': f'Bearer {session.accessJwt}'})

        self.me = await self.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(session.handle))

        return self.me

    async def send_post(
        self,
        text: str,
        profile_identify: Optional[str] = None,
        reply_to: Optional[Union[models.AppBskyFeedPost.ReplyRef, models.AppBskyFeedDefs.ReplyRef]] = None,
        embed: Optional[
            Union[
                'models.AppBskyEmbedImages.Main',
                'models.AppBskyEmbedExternal.Main',
                'models.AppBskyEmbedRecord.Main',
                'models.AppBskyEmbedRecordWithMedia.Main',
            ]
        ] = None,
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        return await self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=repo,
                collection='app.bsky.feed.post',
                record=models.AppBskyFeedPost.Main(
                    createdAt=datetime.now().isoformat(), text=text, reply=reply_to, embed=embed
                ),
            )
        )
