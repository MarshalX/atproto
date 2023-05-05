from datetime import datetime
from typing import Optional, Union

from xrpc_client import models
from xrpc_client.client.raw import ClientRaw


class Client(ClientRaw):
    """High-level client for XRPC of ATProto."""

    def __init__(self):
        super().__init__()
        self.me = None

    def login(self, login: str, password: str) -> models.AppBskyActorGetProfile.ResponseRef:
        session = self.com.atproto.server.create_session(models.ComAtprotoServerCreateSession.Data(login, password))
        self.request.set_additional_headers({'Authorization': f'Bearer {session.accessJwt}'})

        self.me = self.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(session.handle))

        return self.me

    def send_post(
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

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=repo,
                collection='app.bsky.feed.post',
                record=models.AppBskyFeedPost.Main(
                    createdAt=datetime.now().isoformat(), text=text, reply=reply_to, embed=embed
                ),
            )
        )

    def send_image(
        self,
        text: str,
        image: bytes,
        image_alt: str,
        profile_identify: Optional[str] = None,
        reply_to: Optional[Union[models.AppBskyFeedPost.ReplyRef, models.AppBskyFeedDefs.ReplyRef]] = None,
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        upload = self.com.atproto.repo.upload_blob(image)
        images = [models.AppBskyEmbedImages.Image(alt=image_alt, image=upload.blob)]
        return self.send_post(
            text,
            profile_identify=profile_identify,
            reply_to=reply_to,
            embed=models.AppBskyEmbedImages.Main(images=images),
        )

    def like(self, subject: models.ComAtprotoRepoStrongRef.Main) -> models.ComAtprotoRepoCreateRecord.Response:
        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=self.me.did,
                collection='app.bsky.feed.like',
                record=models.AppBskyFeedLike.Main(createdAt=datetime.now().isoformat(), subject=subject),
            )
        )

    def unlike(self, record_key: str, profile_identify: Optional[str] = None) -> int:
        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        return self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection='app.bsky.feed.like',
                repo=repo,
                rkey=record_key,
            )
        )
