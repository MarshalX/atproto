from datetime import datetime
from typing import Optional, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.client.raw import ClientRaw


class Client(ClientRaw):
    """High-level client for XRPC of ATProto."""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.me = None

    def login(self, login: str, password: str) -> models.AppBskyActorGetProfile.ResponseRef:
        """Authorize client and get profile info.

        Args:
            login: Handle/username of the account.
            password: Password of the account. Could be app specific one.

        Returns:
            :obj:`models.AppBskyActorGetProfile.ResponseRef`: Profile information.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

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
        """Send post.

        Note:
            If `profile_identify` is not provided will be sent to the current profile.

        Args:
            text: Text of the post.
            profile_identify: Handle or DID. Where to send post.
            reply_to: Root and parent of the post to reply to.
            embed: Embed models that should be attached to the post.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created post record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

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
        """Send post with attached image.

        Note:
            If `profile_identify` is not provided will be sent to the current profile.

        Args:
            text: Text of the post.
            image: Binary image to attach.
            image_alt: Text version of the image
            profile_identify: Handle or DID. Where to send post.
            reply_to: Root and parent of the post to reply to.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created post record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        upload = self.com.atproto.repo.upload_blob(image)
        images = [models.AppBskyEmbedImages.Image(alt=image_alt, image=upload.blob)]
        return self.send_post(
            text,
            profile_identify=profile_identify,
            reply_to=reply_to,
            embed=models.AppBskyEmbedImages.Main(images=images),
        )

    def like(self, subject: models.ComAtprotoRepoStrongRef.Main) -> models.ComAtprotoRepoCreateRecord.Response:
        """Like the post.

        Args:
            subject: Reference to the post that should be liked.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created like record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=self.me.did,
                collection='app.bsky.feed.like',
                record=models.AppBskyFeedLike.Main(createdAt=datetime.now().isoformat(), subject=subject),
            )
        )

    def unlike(self, record_key: str, profile_identify: Optional[str] = None) -> bool:
        """Unlike the post.

        Args:
            record_key: ID (slog) of the post.
            profile_identify: Handler or DID. Who did the like.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

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
