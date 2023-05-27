import typing as t
from datetime import datetime
from threading import Lock

from atproto.xrpc_client import models
from atproto.xrpc_client.client.methods_mixin import SessionMethodsMixin
from atproto.xrpc_client.client.raw import ClientRaw
from atproto.xrpc_client.models import ids

if t.TYPE_CHECKING:
    from atproto.xrpc_client.client.auth import JwtPayload
    from atproto.xrpc_client.client.base import InvokeType
    from atproto.xrpc_client.request import Response


class Client(ClientRaw, SessionMethodsMixin):
    """High-level client for XRPC of ATProto."""

    def __init__(self, base_url: str = None) -> None:
        super().__init__(base_url)

        self._access_jwt: t.Optional[str] = None
        self._access_jwt_payload: t.Optional['JwtPayload'] = None

        self._refresh_jwt: t.Optional[str] = None
        self._refresh_jwt_payload: t.Optional['JwtPayload'] = None

        self._refresh_lock = Lock()

        self.me: t.Optional[models.AppBskyActorDefs.ProfileViewDetailed] = None

    def _invoke(self, invoke_type: 'InvokeType', **kwargs) -> 'Response':
        session_refreshing = kwargs.pop('session_refreshing', False)
        if session_refreshing:
            return super()._invoke(invoke_type, **kwargs)

        with self._refresh_lock:
            if self._access_jwt and self._should_refresh_session():
                self._refresh_and_set_session()

        return super()._invoke(invoke_type, **kwargs)

    def _get_and_set_session(self, login: str, password: str) -> models.ComAtprotoServerCreateSession.Response:
        session = self.com.atproto.server.create_session(models.ComAtprotoServerCreateSession.Data(login, password))
        self._set_session(session)

        return session

    def _refresh_and_set_session(self) -> models.ComAtprotoServerRefreshSession.Response:
        refresh_session = self.com.atproto.server.refresh_session(
            headers=self._get_auth_headers(self._refresh_jwt), session_refreshing=True
        )
        self._set_session(refresh_session)

        return refresh_session

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

        session = self._get_and_set_session(login, password)
        self.me = self.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(session.handle))

        return self.me

    def send_post(
        self,
        text: str,
        profile_identify: t.Optional[str] = None,
        reply_to: t.Optional[t.Union[models.AppBskyFeedPost.ReplyRef, models.AppBskyFeedDefs.ReplyRef]] = None,
        embed: t.Optional[
            t.Union[
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
                collection=ids.AppBskyFeedPost,
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
        profile_identify: t.Optional[str] = None,
        reply_to: t.Optional[t.Union[models.AppBskyFeedPost.ReplyRef, models.AppBskyFeedDefs.ReplyRef]] = None,
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
                collection=ids.AppBskyFeedLike,
                record=models.AppBskyFeedLike.Main(createdAt=datetime.now().isoformat(), subject=subject),
            )
        )

    def unlike(self, record_key: str, profile_identify: t.Optional[str] = None) -> bool:
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
                collection=ids.AppBskyFeedLike,
                repo=repo,
                rkey=record_key,
            )
        )

    def repost(
        self,
        subject: models.ComAtprotoRepoStrongRef.Main,
        profile_identify: t.Optional[str] = None,
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        """Repost post.

        Note:
            If `profile_identify` is not provided will be sent to the current profile.

        Args:
            subject: Reference to the post that should be reposted.
            profile_identify: Handle or DID. Where to make repost.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the reposted post record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=repo,
                collection=ids.AppBskyFeedRepost,
                record=models.AppBskyFeedRepost.Main(
                    createdAt=datetime.now().isoformat(),
                    subject=subject,
                ),
            )
        )

    def delete_post(self, post_rkey: str, profile_identify: t.Optional[str] = None) -> bool:
        """Delete post.

        Args:
            post_rkey: ID (slug) of the post.
            profile_identify: Handler or DID. Who created the post.

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
                collection=ids.AppBskyFeedPost,
                repo=repo,
                rkey=post_rkey,
            )
        )
