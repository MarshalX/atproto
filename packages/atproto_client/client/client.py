import typing as t
from threading import Lock

from atproto_core.uri import AtUri

from atproto_client import models
from atproto_client.client.methods_mixin import SessionMethodsMixin, TimeMethodsMixin
from atproto_client.client.raw import ClientRaw
from atproto_client.models import ids
from atproto_client.models.languages import DEFAULT_LANGUAGE_CODE1
from atproto_client.utils import TextBuilder

if t.TYPE_CHECKING:
    from atproto_client.client.base import InvokeType
    from atproto_client.request import Response


class Client(SessionMethodsMixin, TimeMethodsMixin, ClientRaw):
    """High-level client for XRPC of ATProto."""

    def __init__(self, base_url: t.Optional[str] = None, *args, **kwargs: t.Any) -> None:
        super().__init__(base_url, *args, **kwargs)

        self._refresh_lock = Lock()

        self.me: t.Optional[models.AppBskyActorDefs.ProfileViewDetailed] = None

    def _invoke(self, invoke_type: 'InvokeType', **kwargs: t.Any) -> 'Response':
        session_refreshing = kwargs.pop('session_refreshing', False)
        if session_refreshing:
            return super()._invoke(invoke_type, **kwargs)

        with self._refresh_lock:
            if self._access_jwt and self._should_refresh_session():
                self._refresh_and_set_session()

        return super()._invoke(invoke_type, **kwargs)

    def _get_and_set_session(self, login: str, password: str) -> models.ComAtprotoServerCreateSession.Response:
        session = self.com.atproto.server.create_session(
            models.ComAtprotoServerCreateSession.Data(identifier=login, password=password)
        )
        self._set_session(session)

        return session

    def _refresh_and_set_session(self) -> models.ComAtprotoServerRefreshSession.Response:
        refresh_session = self.com.atproto.server.refresh_session(
            headers=self._get_auth_headers(self._refresh_jwt), session_refreshing=True
        )
        self._set_session(refresh_session)

        return refresh_session

    def login(
        self, login: t.Optional[str] = None, password: t.Optional[str] = None, session_string: t.Optional[str] = None
    ) -> models.AppBskyActorDefs.ProfileViewDetailed:
        """Authorize a client and get profile info.

        Args:
            login: Handle/username of the account.
            password: Main or app-specific password of the account.
            session_string: Session string (use :py:attr:`~export_session_string` to obtain it).

        Note:
            Either `session_string` or `login` and `password` should be provided.

        Returns:
            :obj:`models.AppBskyActorDefs.ProfileViewDetailed`: Profile information.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        if session_string:
            session = self._import_session_string(session_string)
        elif login and password:
            session = self._get_and_set_session(login, password)
        else:
            raise ValueError('Either session_string or login and password should be provided.')

        self.me = self.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=session.handle))
        return self.me

    def send_post(
        self,
        text: t.Union[str, TextBuilder],
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
        langs: t.Optional[t.List[str]] = None,
        facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None,
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        """Send post.

        Note:
            If `profile_identify` is not provided will be sent to the current profile.

            The default language is ``en``.
            Available languages are defined in :py:mod:`atproto.xrpc_client.models.languages`.

        Args:
            text: Text of the post.
            profile_identify: Handle or DID. Where to send post.
            reply_to: Root and parent of the post to reply to.
            embed: Embed models that should be attached to the post.
            langs: List of used languages in the post.
            facets: List of facets (rich text items).

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created post record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        if isinstance(text, TextBuilder):
            facets = text.build_facets()
            text = text.build_text()

        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        if not langs:
            langs = [DEFAULT_LANGUAGE_CODE1]

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=repo,
                collection=ids.AppBskyFeedPost,
                record=models.AppBskyFeedPost.Main(
                    created_at=self.get_current_time_iso(),
                    text=text,
                    reply=reply_to,
                    embed=embed,
                    langs=langs,
                    facets=facets,
                ),
            )
        )

    def delete_post(self, post_uri: str) -> bool:
        """Delete post.

        Args:
            post_uri: AT URI of the post.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        uri = AtUri.from_str(post_uri)
        return self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyFeedPost,
                repo=uri.hostname,
                rkey=uri.rkey,
            )
        )

    def send_image(
        self,
        text: t.Union[str, TextBuilder],
        image: bytes,
        image_alt: str,
        profile_identify: t.Optional[str] = None,
        reply_to: t.Optional[t.Union[models.AppBskyFeedPost.ReplyRef, models.AppBskyFeedDefs.ReplyRef]] = None,
        langs: t.Optional[t.List[str]] = None,
        facets: t.Optional[t.List['models.AppBskyRichtextFacet.Main']] = None,
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
            langs: List of used languages in the post.
            facets: List of facets (rich text items).

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
            langs=langs,
            facets=facets,
        )

    def get_post(
        self, post_rkey: str, profile_identify: t.Optional[str] = None, cid: t.Optional[str] = None
    ) -> models.ComAtprotoRepoGetRecord.Response:
        """Get post.

        Args:
            post_rkey: ID (slug) of the post.
            profile_identify: Handler or DID. Who created the post.
            cid: The CID of the version of the post.

        Returns:
            :obj:`models.ComAtprotoRepoGetRecord.Response`: Post.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        repo = self.me.did
        if profile_identify:
            repo = profile_identify

        return self.com.atproto.repo.get_record(
            models.ComAtprotoRepoGetRecord.Params(
                collection=ids.AppBskyFeedPost,
                repo=repo,
                rkey=post_rkey,
                cid=cid,
            )
        )

    def get_posts(self, uris: t.List[str]) -> models.AppBskyFeedGetPosts.Response:
        """Get posts.

        Args:
            uris: Uris (AT URI).

        Example:
            .. code-block:: python

                client.get_posts(['at://did:plc:kvwvcn5iqfooopmyzvb4qzba/app.bsky.feed.post/3k2yihcrp6f2c'])

        Returns:
            :obj:`models.AppBskyFeedGetPosts.Response`: Posts.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_posts(
            models.AppBskyFeedGetPosts.Params(
                uris=uris,
            )
        )

    def get_post_thread(
        self, uri: str, depth: t.Optional[int] = None, parent_height: t.Optional[int] = None
    ) -> models.AppBskyFeedGetPostThread.Response:
        """Get post thread.

        Args:
            uri: AT URI.

        Returns:
            :obj:`models.AppBskyFeedGetPostThread.Response`: Post thread.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_post_thread(
            models.AppBskyFeedGetPostThread.Params(
                uri=uri,
                depth=depth,
                parent_height=parent_height,
            )
        )

    def get_likes(
        self, uri: str, cid: t.Optional[str] = None, cursor: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyFeedGetLikes.Response:
        """Get likes.

        Args:
            uri: AT URI.
            cid: CID.
            cursor: Cursor of the last like in the previous page.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyFeedGetLikes.Response`: Likes.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_likes(
            models.AppBskyFeedGetLikes.Params(uri=uri, cid=cid, cursor=cursor, limit=limit)
        )

    def get_reposted_by(
        self, uri: str, cid: t.Optional[str] = None, cursor: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyFeedGetRepostedBy.Response:
        """Get reposted by (reposts).

        Args:
            uri: AT URI.
            cid: CID.
            cursor: Cursor of the last like in the previous page.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyFeedGetRepostedBy.Response`: Reposts.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_reposted_by(
            models.AppBskyFeedGetRepostedBy.Params(uri=uri, cid=cid, cursor=cursor, limit=limit)
        )

    def get_timeline(
        self, algorithm: t.Optional[str] = None, cursor: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyFeedGetTimeline.Response:
        """Get home timeline.

        Args:
            algorithm: Algorithm.
            cursor: Cursor of the last like in the previous page.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyFeedGetTimeline.Response`: Home timeline.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_timeline(
            models.AppBskyFeedGetTimeline.Params(algorithm=algorithm, cursor=cursor, limit=limit)
        )

    def get_author_feed(
        self, actor: str, cursor: t.Optional[str] = None, filter: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyFeedGetAuthorFeed.Response:
        """Get author (profile) feed.

        Args:
            actor: Actor (handle or DID).
            cursor: Cursor of the last like in the previous page.
            filter: Filter.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyFeedGetAuthorFeed.Response`: Feed.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.feed.get_author_feed(
            models.AppBskyFeedGetAuthorFeed.Params(actor=actor, cursor=cursor, fitler=filter, limit=limit)
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
                record=models.AppBskyFeedLike.Main(created_at=self.get_current_time_iso(), subject=subject),
            )
        )

    def unlike(self, like_uri: str) -> bool:
        """Unlike the post.

        Args:
            like_uri: AT URI of the like.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        uri = AtUri.from_str(like_uri)
        return self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyFeedLike,
                repo=uri.hostname,
                rkey=uri.rkey,
            )
        )

    def repost(
        self,
        subject: models.ComAtprotoRepoStrongRef.Main,
    ) -> models.ComAtprotoRepoCreateRecord.Response:
        """Repost post.

        Args:
            subject: Reference to the post that should be reposted.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the reposted post record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=self.me.did,
                collection=ids.AppBskyFeedRepost,
                record=models.AppBskyFeedRepost.Main(
                    created_at=self.get_current_time_iso(),
                    subject=subject,
                ),
            )
        )

    def unrepost(self, repost_uri: str) -> bool:
        """Unrepost the post (delete repost).

        Args:
            repost_uri: AT URI of the repost.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        uri = AtUri.from_str(repost_uri)
        return self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyFeedRepost,
                repo=uri.hostname,
                rkey=uri.rkey,
            )
        )

    def follow(self, subject: str) -> models.ComAtprotoRepoCreateRecord.Response:
        """Follow the profile.

        Args:
            subject: DID of the profile.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created follow record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=self.me.did,
                collection=ids.AppBskyGraphFollow,
                record=models.AppBskyGraphFollow.Main(created_at=self.get_current_time_iso(), subject=subject),
            )
        )

    def unfollow(self, follow_uri: str) -> bool:
        """Unfollow the profile.

        Args:
            follow_uri: AT URI of the follow.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        uri = AtUri.from_str(follow_uri)
        return self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyGraphFollow,
                repo=uri.hostname,
                rkey=uri.rkey,
            )
        )

    def get_follows(
        self, actor: str, cursor: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyGraphGetFollows.Response:
        """Get follows of the profile.

        Args:
            actor: Actor (handle or DID).
            cursor: Cursor of the last like in the previous page.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyGraphGetFollows.Response`: Follows.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.graph.get_follows(
            models.AppBskyGraphGetFollows.Params(actor=actor, cursor=cursor, limit=limit)
        )

    def get_followers(
        self, actor: str, cursor: t.Optional[str] = None, limit: t.Optional[int] = None
    ) -> models.AppBskyGraphGetFollowers.Response:
        """Get followers of the profile.

        Args:
            actor: Actor (handle or DID).
            cursor: Cursor of the last like in the previous page.
            limit: Limit count of likes to return.

        Returns:
            :obj:`models.AppBskyGraphGetFollowers.Response`: Followers.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.graph.get_followers(
            models.AppBskyGraphGetFollowers.Params(actor=actor, cursor=cursor, limit=limit)
        )

    def get_profile(self, actor: str) -> models.AppBskyActorDefs.ProfileViewDetailed:
        """Get profile.

        Args:
            actor: Actor (handle or DID).

        Returns:
            :obj:`models.AppBskyActorDefs.ProfileViewDetailed`: Profile.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=actor))

    def get_profiles(self, actors: t.List[str]) -> models.AppBskyActorGetProfiles.Response:
        """Get profiles.

        Args:
            actors: List of actors (handles or DIDs).

        Returns:
            :obj:`models.AppBskyActorGetProfiles.Response`: Profiles.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.actor.get_profiles(models.AppBskyActorGetProfiles.Params(actors=actors))

    def mute(self, actor: str) -> bool:
        """Mute actor (profile).

        Args:
            actor: Actor (handle or DID).

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.graph.mute_actor(models.AppBskyGraphMuteActor.Data(actor=actor))

    def unmute(self, actor: str) -> bool:
        """Unmute actor (profile).

        Args:
            actor: Actor (handle or DID).

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.app.bsky.graph.unmute_actor(models.AppBskyGraphUnmuteActor.Data(actor=actor))

    def resolve_handle(self, handle: str) -> models.ComAtprotoIdentityResolveHandle.Response:
        """Resolve the handle.

        Args:
            handle: Handle.

        Returns:
            :obj:`models.ComAtprotoIdentityResolveHandle.Response`: Resolved handle (DID).

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.identity.resolve_handle(models.ComAtprotoIdentityResolveHandle.Params(handle=handle))

    def update_handle(self, handle: str) -> bool:
        """Update the handle.

        Args:
            handle: New handle.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.identity.update_handle(models.ComAtprotoIdentityUpdateHandle.Data(handle=handle))

    def upload_blob(self, data: bytes) -> models.ComAtprotoRepoUploadBlob.Response:
        """Upload blob.

        Args:
            data: Binary data.

        Returns:
            :obj:`models.ComAtprotoRepoUploadBlob.Response`: Uploaded blob reference.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return self.com.atproto.repo.upload_blob(data)

    #: Alias for :attr:`unfollow`
    delete_follow = unfollow
    #: Alias for :attr:`unlike`
    delete_like = unlike
    #: Alias for :attr:`unrepost`
    delete_repost = unrepost
    #: Alias for :attr:`send_post`
    post = send_post
    #: Alias for :attr:`delete_post`
    unsend = delete_post
