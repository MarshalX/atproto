##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################

import typing as t
from asyncio import Lock

from atproto.utils import TextBuilder
from atproto.xrpc_client import models
from atproto.xrpc_client.client.async_raw import AsyncClientRaw
from atproto.xrpc_client.client.methods_mixin import SessionMethodsMixin, TimeMethodsMixin
from atproto.xrpc_client.models import ids
from atproto.xrpc_client.models.languages import DEFAULT_LANGUAGE_CODE1

if t.TYPE_CHECKING:
    from atproto.xrpc_client.client.base import InvokeType
    from atproto.xrpc_client.request import Response


class AsyncClient(SessionMethodsMixin, TimeMethodsMixin, AsyncClientRaw):
    """High-level client for XRPC of ATProto."""

    def __init__(self, base_url: t.Optional[str] = None, *args, **kwargs) -> None:
        super().__init__(base_url, *args, **kwargs)

        self._refresh_lock = Lock()

        self.me: t.Optional[models.AppBskyActorDefs.ProfileViewDetailed] = None

    async def _invoke(self, invoke_type: 'InvokeType', **kwargs) -> 'Response':
        session_refreshing = kwargs.pop('session_refreshing', False)
        if session_refreshing:
            return await super()._invoke(invoke_type, **kwargs)

        async with self._refresh_lock:
            if self._access_jwt and self._should_refresh_session():
                await self._refresh_and_set_session()

        return await super()._invoke(invoke_type, **kwargs)

    async def _get_and_set_session(self, login: str, password: str) -> models.ComAtprotoServerCreateSession.Response:
        session = await self.com.atproto.server.create_session(
            models.ComAtprotoServerCreateSession.Data(identifier=login, password=password)
        )
        self._set_session(session)

        return session

    async def _refresh_and_set_session(self) -> models.ComAtprotoServerRefreshSession.Response:
        refresh_session = await self.com.atproto.server.refresh_session(
            headers=self._get_auth_headers(self._refresh_jwt), session_refreshing=True
        )
        self._set_session(refresh_session)

        return refresh_session

    async def login(
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
            session = await self._get_and_set_session(login, password)
        else:
            raise ValueError('Either session_string or login and password should be provided.')

        self.me = await self.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=session.handle))
        return self.me

    async def send_post(
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

            The async default language is ``en``.
            Available languages are async defined in :py:mod:`atproto.xrpc_client.models.languages`.

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

        return await self.com.atproto.repo.create_record(
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

    async def send_image(
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

        upload = await self.com.atproto.repo.upload_blob(image)
        images = [models.AppBskyEmbedImages.Image(alt=image_alt, image=upload.blob)]
        return await self.send_post(
            text,
            profile_identify=profile_identify,
            reply_to=reply_to,
            embed=models.AppBskyEmbedImages.Main(images=images),
            langs=langs,
            facets=facets,
        )

    async def like(self, subject: models.ComAtprotoRepoStrongRef.Main) -> models.ComAtprotoRepoCreateRecord.Response:
        """Like the post.

        Args:
            subject: Reference to the post that should be liked.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Reference to the created like record.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        return await self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=self.me.did,
                collection=ids.AppBskyFeedLike,
                record=models.AppBskyFeedLike.Main(created_at=self.get_current_time_iso(), subject=subject),
            )
        )

    async def unlike(self, record_key: str, profile_identify: t.Optional[str] = None) -> bool:
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

        return await self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyFeedLike,
                repo=repo,
                rkey=record_key,
            )
        )

    async def repost(
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

        return await self.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=repo,
                collection=ids.AppBskyFeedRepost,
                record=models.AppBskyFeedRepost.Main(
                    created_at=self.get_current_time_iso(),
                    subject=subject,
                ),
            )
        )

    async def delete_post(self, post_rkey: str, profile_identify: t.Optional[str] = None) -> bool:
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

        return await self.com.atproto.repo.delete_record(
            models.ComAtprotoRepoDeleteRecord.Data(
                collection=ids.AppBskyFeedPost,
                repo=repo,
                rkey=post_rkey,
            )
        )
