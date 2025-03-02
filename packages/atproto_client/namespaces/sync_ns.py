##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto_client import models
from atproto_client.models.utils import get_or_create, get_response_model
from atproto_client.namespaces.base import NamespaceBase, RecordBase

if t.TYPE_CHECKING:
    from atproto_client.client.raw import ClientRaw


class AppNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.bsky = AppBskyNamespace(self._client)


class AppBskyNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.actor = AppBskyActorNamespace(self._client)
        self.feed = AppBskyFeedNamespace(self._client)
        self.graph = AppBskyGraphNamespace(self._client)
        self.labeler = AppBskyLabelerNamespace(self._client)
        self.notification = AppBskyNotificationNamespace(self._client)
        self.unspecced = AppBskyUnspeccedNamespace(self._client)
        self.video = AppBskyVideoNamespace(self._client)


class AppBskyActorProfileRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyActorProfile.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorProfile.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.actor.profile', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyActorProfile.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyActorProfile.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorProfile.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorProfile.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.actor.profile',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyActorProfile.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyActorProfile.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyActorProfile.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorProfile.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorProfile.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.actor.profile',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyActorProfile.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.actor.profile',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyActorNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.profile = AppBskyActorProfileRecord(self._client)

    def get_preferences(
        self,
        params: t.Optional[
            t.Union[models.AppBskyActorGetPreferences.Params, models.AppBskyActorGetPreferences.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorGetPreferences.Response':
        """Get private preferences attached to the current account. Expected use is synchronization between multiple devices, and import/export during account migration. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetPreferences.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorGetPreferences.Params', get_or_create(params, models.AppBskyActorGetPreferences.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.actor.getPreferences', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetPreferences.Response)

    def get_profile(
        self,
        params: t.Union[models.AppBskyActorGetProfile.Params, models.AppBskyActorGetProfile.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorDefs.ProfileViewDetailed':
        """Get detailed profile view of an actor. Does not require auth, but contains relevant metadata with auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorDefs.ProfileViewDetailed`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorGetProfile.Params', get_or_create(params, models.AppBskyActorGetProfile.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.actor.getProfile', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorDefs.ProfileViewDetailed)

    def get_profiles(
        self,
        params: t.Union[models.AppBskyActorGetProfiles.Params, models.AppBskyActorGetProfiles.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorGetProfiles.Response':
        """Get detailed profile views of multiple actors.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetProfiles.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorGetProfiles.Params', get_or_create(params, models.AppBskyActorGetProfiles.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.actor.getProfiles', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetProfiles.Response)

    def get_suggestions(
        self,
        params: t.Optional[
            t.Union[models.AppBskyActorGetSuggestions.Params, models.AppBskyActorGetSuggestions.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorGetSuggestions.Response':
        """Get a list of suggested actors. Expected use is discovery of accounts to follow during new account onboarding.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetSuggestions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorGetSuggestions.Params', get_or_create(params, models.AppBskyActorGetSuggestions.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.actor.getSuggestions', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetSuggestions.Response)

    def put_preferences(
        self,
        data: t.Union[models.AppBskyActorPutPreferences.Data, models.AppBskyActorPutPreferences.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Set the private preferences attached to the account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyActorPutPreferences.Data', get_or_create(data, models.AppBskyActorPutPreferences.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.actor.putPreferences', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def search_actors(
        self,
        params: t.Optional[
            t.Union[models.AppBskyActorSearchActors.Params, models.AppBskyActorSearchActors.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorSearchActors.Response':
        """Find actors (profiles) matching search criteria. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActors.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorSearchActors.Params', get_or_create(params, models.AppBskyActorSearchActors.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.actor.searchActors', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActors.Response)

    def search_actors_typeahead(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyActorSearchActorsTypeahead.Params, models.AppBskyActorSearchActorsTypeahead.ParamsDict
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyActorSearchActorsTypeahead.Response':
        """Find actor suggestions for a prefix search term. Expected use is for auto-completion during text field entry. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActorsTypeahead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyActorSearchActorsTypeahead.Params',
            get_or_create(params, models.AppBskyActorSearchActorsTypeahead.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.actor.searchActorsTypeahead', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActorsTypeahead.Response)


class AppBskyFeedGeneratorRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedGenerator.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGenerator.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.generator', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedGenerator.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedGenerator.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGenerator.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGenerator.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.generator',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedGenerator.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedGenerator.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedGenerator.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGenerator.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGenerator.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.generator',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedGenerator.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.generator',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedLikeRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedLike.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedLike.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.like', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedLike.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedLike.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedLike.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedLike.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.like',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedLike.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedLike.Record', record.value) for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedLike.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedLike.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedLike.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.like',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedLike.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.like',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedPostRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedPost.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPost.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.post', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedPost.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedPost.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedPost.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPost.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.post',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedPost.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedPost.Record', record.value) for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedPost.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedPost.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPost.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.post',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedPost.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.post',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedPostgateRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedPostgate.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPostgate.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.postgate', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedPostgate.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedPostgate.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedPostgate.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPostgate.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.postgate',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedPostgate.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedPostgate.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedPostgate.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedPostgate.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedPostgate.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.postgate',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedPostgate.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.postgate',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedRepostRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedRepost.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedRepost.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.repost', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedRepost.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedRepost.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedRepost.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedRepost.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.repost',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedRepost.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedRepost.Record', record.value) for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedRepost.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedRepost.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedRepost.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.repost',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedRepost.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.repost',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedThreadgateRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyFeedThreadgate.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedThreadgate.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.feed.threadgate', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyFeedThreadgate.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyFeedThreadgate.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedThreadgate.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedThreadgate.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.feed.threadgate',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyFeedThreadgate.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyFeedThreadgate.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyFeedThreadgate.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedThreadgate.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedThreadgate.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.feed.threadgate',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyFeedThreadgate.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.feed.threadgate',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyFeedNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.generator = AppBskyFeedGeneratorRecord(self._client)
        self.like = AppBskyFeedLikeRecord(self._client)
        self.post = AppBskyFeedPostRecord(self._client)
        self.postgate = AppBskyFeedPostgateRecord(self._client)
        self.repost = AppBskyFeedRepostRecord(self._client)
        self.threadgate = AppBskyFeedThreadgateRecord(self._client)

    def describe_feed_generator(self, **kwargs: t.Any) -> 'models.AppBskyFeedDescribeFeedGenerator.Response':
        """Get information about a feed generator, including policies and offered feed URIs. Does not require auth; implemented by Feed Generator services (not App View).

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedDescribeFeedGenerator.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'app.bsky.feed.describeFeedGenerator', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedDescribeFeedGenerator.Response)

    def get_actor_feeds(
        self,
        params: t.Union[models.AppBskyFeedGetActorFeeds.Params, models.AppBskyFeedGetActorFeeds.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetActorFeeds.Response':
        """Get a list of feeds (feed generator records) created by the actor (in the actor's repo).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetActorFeeds.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetActorFeeds.Params', get_or_create(params, models.AppBskyFeedGetActorFeeds.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getActorFeeds', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetActorFeeds.Response)

    def get_actor_likes(
        self,
        params: t.Union[models.AppBskyFeedGetActorLikes.Params, models.AppBskyFeedGetActorLikes.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetActorLikes.Response':
        """Get a list of posts liked by an actor. Requires auth, actor must be the requesting account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetActorLikes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetActorLikes.Params', get_or_create(params, models.AppBskyFeedGetActorLikes.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getActorLikes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetActorLikes.Response)

    def get_author_feed(
        self,
        params: t.Union[models.AppBskyFeedGetAuthorFeed.Params, models.AppBskyFeedGetAuthorFeed.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetAuthorFeed.Response':
        """Get a view of an actor's 'author feed' (post and reposts by the author). Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetAuthorFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetAuthorFeed.Params', get_or_create(params, models.AppBskyFeedGetAuthorFeed.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getAuthorFeed', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetAuthorFeed.Response)

    def get_feed(
        self, params: t.Union[models.AppBskyFeedGetFeed.Params, models.AppBskyFeedGetFeed.ParamsDict], **kwargs: t.Any
    ) -> 'models.AppBskyFeedGetFeed.Response':
        """Get a hydrated feed from an actor's selected feed generator. Implemented by App View.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetFeed.Params', get_or_create(params, models.AppBskyFeedGetFeed.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getFeed', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeed.Response)

    def get_feed_generator(
        self,
        params: t.Union[models.AppBskyFeedGetFeedGenerator.Params, models.AppBskyFeedGetFeedGenerator.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetFeedGenerator.Response':
        """Get information about a feed generator. Implemented by AppView.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeedGenerator.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetFeedGenerator.Params',
            get_or_create(params, models.AppBskyFeedGetFeedGenerator.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedGenerator', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedGenerator.Response)

    def get_feed_generators(
        self,
        params: t.Union[models.AppBskyFeedGetFeedGenerators.Params, models.AppBskyFeedGetFeedGenerators.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetFeedGenerators.Response':
        """Get information about a list of feed generators.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeedGenerators.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetFeedGenerators.Params',
            get_or_create(params, models.AppBskyFeedGetFeedGenerators.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedGenerators', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedGenerators.Response)

    def get_feed_skeleton(
        self,
        params: t.Union[models.AppBskyFeedGetFeedSkeleton.Params, models.AppBskyFeedGetFeedSkeleton.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetFeedSkeleton.Response':
        """Get a skeleton of a feed provided by a feed generator. Auth is optional, depending on provider requirements, and provides the DID of the requester. Implemented by Feed Generator Service.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeedSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetFeedSkeleton.Params', get_or_create(params, models.AppBskyFeedGetFeedSkeleton.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedSkeleton', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedSkeleton.Response)

    def get_likes(
        self, params: t.Union[models.AppBskyFeedGetLikes.Params, models.AppBskyFeedGetLikes.ParamsDict], **kwargs: t.Any
    ) -> 'models.AppBskyFeedGetLikes.Response':
        """Get like records which reference a subject (by AT-URI and CID).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetLikes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetLikes.Params', get_or_create(params, models.AppBskyFeedGetLikes.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getLikes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetLikes.Response)

    def get_list_feed(
        self,
        params: t.Union[models.AppBskyFeedGetListFeed.Params, models.AppBskyFeedGetListFeed.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetListFeed.Response':
        """Get a feed of recent posts from a list (posts and reposts from any actors on the list). Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetListFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetListFeed.Params', get_or_create(params, models.AppBskyFeedGetListFeed.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getListFeed', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetListFeed.Response)

    def get_post_thread(
        self,
        params: t.Union[models.AppBskyFeedGetPostThread.Params, models.AppBskyFeedGetPostThread.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetPostThread.Response':
        """Get posts in a thread. Does not require auth, but additional metadata and filtering will be applied for authed requests.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPostThread.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetPostThread.Params', get_or_create(params, models.AppBskyFeedGetPostThread.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getPostThread', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPostThread.Response)

    def get_posts(
        self, params: t.Union[models.AppBskyFeedGetPosts.Params, models.AppBskyFeedGetPosts.ParamsDict], **kwargs: t.Any
    ) -> 'models.AppBskyFeedGetPosts.Response':
        """Gets post views for a specified list of posts (by AT-URI). This is sometimes referred to as 'hydrating' a 'feed skeleton'.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPosts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetPosts.Params', get_or_create(params, models.AppBskyFeedGetPosts.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getPosts', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPosts.Response)

    def get_quotes(
        self,
        params: t.Union[models.AppBskyFeedGetQuotes.Params, models.AppBskyFeedGetQuotes.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetQuotes.Response':
        """Get a list of quotes for a given post.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetQuotes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetQuotes.Params', get_or_create(params, models.AppBskyFeedGetQuotes.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getQuotes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetQuotes.Response)

    def get_reposted_by(
        self,
        params: t.Union[models.AppBskyFeedGetRepostedBy.Params, models.AppBskyFeedGetRepostedBy.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetRepostedBy.Response':
        """Get a list of reposts for a given post.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetRepostedBy.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetRepostedBy.Params', get_or_create(params, models.AppBskyFeedGetRepostedBy.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getRepostedBy', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetRepostedBy.Response)

    def get_suggested_feeds(
        self,
        params: t.Optional[
            t.Union[models.AppBskyFeedGetSuggestedFeeds.Params, models.AppBskyFeedGetSuggestedFeeds.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetSuggestedFeeds.Response':
        """Get a list of suggested feeds (feed generators) for the requesting account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetSuggestedFeeds.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetSuggestedFeeds.Params',
            get_or_create(params, models.AppBskyFeedGetSuggestedFeeds.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getSuggestedFeeds', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetSuggestedFeeds.Response)

    def get_timeline(
        self,
        params: t.Optional[
            t.Union[models.AppBskyFeedGetTimeline.Params, models.AppBskyFeedGetTimeline.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedGetTimeline.Response':
        """Get a view of the requesting account's home timeline. This is expected to be some form of reverse-chronological feed.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetTimeline.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedGetTimeline.Params', get_or_create(params, models.AppBskyFeedGetTimeline.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.getTimeline', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetTimeline.Response)

    def search_posts(
        self,
        params: t.Union[models.AppBskyFeedSearchPosts.Params, models.AppBskyFeedSearchPosts.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedSearchPosts.Response':
        """Find posts matching search criteria, returning views of those posts.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedSearchPosts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyFeedSearchPosts.Params', get_or_create(params, models.AppBskyFeedSearchPosts.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.feed.searchPosts', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedSearchPosts.Response)

    def send_interactions(
        self,
        data: t.Union[models.AppBskyFeedSendInteractions.Data, models.AppBskyFeedSendInteractions.DataDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyFeedSendInteractions.Response':
        """Send information about interactions with feed items back to the feed generator that served them.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedSendInteractions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyFeedSendInteractions.Data', get_or_create(data, models.AppBskyFeedSendInteractions.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.feed.sendInteractions',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyFeedSendInteractions.Response)


class AppBskyGraphBlockRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphBlock.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphBlock.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.block', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphBlock.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphBlock.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphBlock.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphBlock.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.block',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphBlock.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphBlock.Record', record.value) for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphBlock.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphBlock.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphBlock.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.block',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphBlock.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.block',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphFollowRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphFollow.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphFollow.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.follow', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphFollow.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphFollow.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphFollow.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphFollow.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.follow',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphFollow.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphFollow.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphFollow.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphFollow.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphFollow.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.follow',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphFollow.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.follow',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphListRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphList.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphList.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.list', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphList.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphList.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphList.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphList.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.list',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphList.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphList.Record', record.value) for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphList.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphList.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphList.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.list',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphList.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.list',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphListblockRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphListblock.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListblock.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.listblock', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphListblock.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphListblock.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphListblock.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListblock.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.listblock',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphListblock.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphListblock.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphListblock.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphListblock.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListblock.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.listblock',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphListblock.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.listblock',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphListitemRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphListitem.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListitem.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.listitem', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphListitem.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphListitem.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphListitem.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListitem.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.listitem',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphListitem.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphListitem.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphListitem.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphListitem.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphListitem.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.listitem',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphListitem.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.listitem',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphStarterpackRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyGraphStarterpack.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphStarterpack.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.graph.starterpack', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyGraphStarterpack.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyGraphStarterpack.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphStarterpack.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphStarterpack.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.graph.starterpack',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyGraphStarterpack.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyGraphStarterpack.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyGraphStarterpack.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphStarterpack.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphStarterpack.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.graph.starterpack',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyGraphStarterpack.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.graph.starterpack',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyGraphNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.block = AppBskyGraphBlockRecord(self._client)
        self.follow = AppBskyGraphFollowRecord(self._client)
        self.list = AppBskyGraphListRecord(self._client)
        self.listblock = AppBskyGraphListblockRecord(self._client)
        self.listitem = AppBskyGraphListitemRecord(self._client)
        self.starterpack = AppBskyGraphStarterpackRecord(self._client)

    def get_actor_starter_packs(
        self,
        params: t.Union[
            models.AppBskyGraphGetActorStarterPacks.Params, models.AppBskyGraphGetActorStarterPacks.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetActorStarterPacks.Response':
        """Get a list of starter packs created by the actor.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetActorStarterPacks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetActorStarterPacks.Params',
            get_or_create(params, models.AppBskyGraphGetActorStarterPacks.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getActorStarterPacks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetActorStarterPacks.Response)

    def get_blocks(
        self,
        params: t.Optional[
            t.Union[models.AppBskyGraphGetBlocks.Params, models.AppBskyGraphGetBlocks.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetBlocks.Response':
        """Enumerates which accounts the requesting account is currently blocking. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetBlocks.Params', get_or_create(params, models.AppBskyGraphGetBlocks.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getBlocks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetBlocks.Response)

    def get_followers(
        self,
        params: t.Union[models.AppBskyGraphGetFollowers.Params, models.AppBskyGraphGetFollowers.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetFollowers.Response':
        """Enumerates accounts which follow a specified account (actor).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollowers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetFollowers.Params', get_or_create(params, models.AppBskyGraphGetFollowers.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getFollowers', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollowers.Response)

    def get_follows(
        self,
        params: t.Union[models.AppBskyGraphGetFollows.Params, models.AppBskyGraphGetFollows.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetFollows.Response':
        """Enumerates accounts which a specified account (actor) follows.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollows.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetFollows.Params', get_or_create(params, models.AppBskyGraphGetFollows.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getFollows', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollows.Response)

    def get_known_followers(
        self,
        params: t.Union[models.AppBskyGraphGetKnownFollowers.Params, models.AppBskyGraphGetKnownFollowers.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetKnownFollowers.Response':
        """Enumerates accounts which follow a specified account (actor) and are followed by the viewer.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetKnownFollowers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetKnownFollowers.Params',
            get_or_create(params, models.AppBskyGraphGetKnownFollowers.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getKnownFollowers', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetKnownFollowers.Response)

    def get_list(
        self, params: t.Union[models.AppBskyGraphGetList.Params, models.AppBskyGraphGetList.ParamsDict], **kwargs: t.Any
    ) -> 'models.AppBskyGraphGetList.Response':
        """Gets a 'view' (with additional context) of a specified list.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetList.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetList.Params', get_or_create(params, models.AppBskyGraphGetList.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getList', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetList.Response)

    def get_list_blocks(
        self,
        params: t.Optional[
            t.Union[models.AppBskyGraphGetListBlocks.Params, models.AppBskyGraphGetListBlocks.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetListBlocks.Response':
        """Get mod lists that the requesting account (actor) is blocking. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetListBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetListBlocks.Params', get_or_create(params, models.AppBskyGraphGetListBlocks.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getListBlocks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetListBlocks.Response)

    def get_list_mutes(
        self,
        params: t.Optional[
            t.Union[models.AppBskyGraphGetListMutes.Params, models.AppBskyGraphGetListMutes.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetListMutes.Response':
        """Enumerates mod lists that the requesting account (actor) currently has muted. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetListMutes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetListMutes.Params', get_or_create(params, models.AppBskyGraphGetListMutes.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getListMutes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetListMutes.Response)

    def get_lists(
        self,
        params: t.Union[models.AppBskyGraphGetLists.Params, models.AppBskyGraphGetLists.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetLists.Response':
        """Enumerates the lists created by a specified account (actor).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetLists.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetLists.Params', get_or_create(params, models.AppBskyGraphGetLists.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getLists', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetLists.Response)

    def get_mutes(
        self,
        params: t.Optional[t.Union[models.AppBskyGraphGetMutes.Params, models.AppBskyGraphGetMutes.ParamsDict]] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetMutes.Response':
        """Enumerates accounts that the requesting account (actor) currently has muted. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetMutes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetMutes.Params', get_or_create(params, models.AppBskyGraphGetMutes.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getMutes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetMutes.Response)

    def get_relationships(
        self,
        params: t.Union[models.AppBskyGraphGetRelationships.Params, models.AppBskyGraphGetRelationships.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetRelationships.Response':
        """Enumerates public relationships between one account, and a list of other accounts. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetRelationships.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetRelationships.Params',
            get_or_create(params, models.AppBskyGraphGetRelationships.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getRelationships', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetRelationships.Response)

    def get_starter_pack(
        self,
        params: t.Union[models.AppBskyGraphGetStarterPack.Params, models.AppBskyGraphGetStarterPack.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetStarterPack.Response':
        """Gets a view of a starter pack.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetStarterPack.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetStarterPack.Params', get_or_create(params, models.AppBskyGraphGetStarterPack.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getStarterPack', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetStarterPack.Response)

    def get_starter_packs(
        self,
        params: t.Union[models.AppBskyGraphGetStarterPacks.Params, models.AppBskyGraphGetStarterPacks.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetStarterPacks.Response':
        """Get views for a list of starter packs.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetStarterPacks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetStarterPacks.Params',
            get_or_create(params, models.AppBskyGraphGetStarterPacks.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getStarterPacks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetStarterPacks.Response)

    def get_suggested_follows_by_actor(
        self,
        params: t.Union[
            models.AppBskyGraphGetSuggestedFollowsByActor.Params,
            models.AppBskyGraphGetSuggestedFollowsByActor.ParamsDict,
        ],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphGetSuggestedFollowsByActor.Response':
        """Enumerates follows similar to a given account (actor). Expected use is to recommend additional accounts immediately after following one account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetSuggestedFollowsByActor.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphGetSuggestedFollowsByActor.Params',
            get_or_create(params, models.AppBskyGraphGetSuggestedFollowsByActor.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.getSuggestedFollowsByActor',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyGraphGetSuggestedFollowsByActor.Response)

    def mute_actor(
        self, data: t.Union[models.AppBskyGraphMuteActor.Data, models.AppBskyGraphMuteActor.DataDict], **kwargs: t.Any
    ) -> bool:
        """Creates a mute relationship for the specified account. Mutes are private in Bluesky. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast('models.AppBskyGraphMuteActor.Data', get_or_create(data, models.AppBskyGraphMuteActor.Data))
        response = self._client.invoke_procedure(
            'app.bsky.graph.muteActor', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def mute_actor_list(
        self,
        data: t.Union[models.AppBskyGraphMuteActorList.Data, models.AppBskyGraphMuteActorList.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Creates a mute relationship for the specified list of accounts. Mutes are private in Bluesky. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyGraphMuteActorList.Data', get_or_create(data, models.AppBskyGraphMuteActorList.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.graph.muteActorList', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def mute_thread(
        self, data: t.Union[models.AppBskyGraphMuteThread.Data, models.AppBskyGraphMuteThread.DataDict], **kwargs: t.Any
    ) -> bool:
        """Mutes a thread preventing notifications from the thread and any of its children. Mutes are private in Bluesky. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyGraphMuteThread.Data', get_or_create(data, models.AppBskyGraphMuteThread.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.graph.muteThread', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def search_starter_packs(
        self,
        params: t.Union[models.AppBskyGraphSearchStarterPacks.Params, models.AppBskyGraphSearchStarterPacks.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyGraphSearchStarterPacks.Response':
        """Find starter packs matching search criteria. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphSearchStarterPacks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyGraphSearchStarterPacks.Params',
            get_or_create(params, models.AppBskyGraphSearchStarterPacks.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.graph.searchStarterPacks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphSearchStarterPacks.Response)

    def unmute_actor(
        self,
        data: t.Union[models.AppBskyGraphUnmuteActor.Data, models.AppBskyGraphUnmuteActor.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Unmutes the specified account. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyGraphUnmuteActor.Data', get_or_create(data, models.AppBskyGraphUnmuteActor.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.graph.unmuteActor', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def unmute_actor_list(
        self,
        data: t.Union[models.AppBskyGraphUnmuteActorList.Data, models.AppBskyGraphUnmuteActorList.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Unmutes the specified list of accounts. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyGraphUnmuteActorList.Data', get_or_create(data, models.AppBskyGraphUnmuteActorList.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.graph.unmuteActorList', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def unmute_thread(
        self,
        data: t.Union[models.AppBskyGraphUnmuteThread.Data, models.AppBskyGraphUnmuteThread.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Unmutes the specified thread. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyGraphUnmuteThread.Data', get_or_create(data, models.AppBskyGraphUnmuteThread.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.graph.unmuteThread', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyLabelerServiceRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.AppBskyLabelerService.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyLabelerService.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='app.bsky.labeler.service', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.AppBskyLabelerService.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.AppBskyLabelerService.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyLabelerService.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyLabelerService.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='app.bsky.labeler.service',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.AppBskyLabelerService.ListRecordsResponse(
            records={
                record.uri: t.cast('models.AppBskyLabelerService.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.AppBskyLabelerService.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.AppBskyLabelerService.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyLabelerService.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='app.bsky.labeler.service',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.AppBskyLabelerService.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='app.bsky.labeler.service',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyLabelerNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.service = AppBskyLabelerServiceRecord(self._client)

    def get_services(
        self,
        params: t.Union[models.AppBskyLabelerGetServices.Params, models.AppBskyLabelerGetServices.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyLabelerGetServices.Response':
        """Get information about a list of labeler services.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyLabelerGetServices.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyLabelerGetServices.Params', get_or_create(params, models.AppBskyLabelerGetServices.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.labeler.getServices', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyLabelerGetServices.Response)


class AppBskyNotificationNamespace(NamespaceBase):
    def get_unread_count(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyNotificationGetUnreadCount.Params, models.AppBskyNotificationGetUnreadCount.ParamsDict
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyNotificationGetUnreadCount.Response':
        """Count the number of unread notifications for the requesting account. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationGetUnreadCount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyNotificationGetUnreadCount.Params',
            get_or_create(params, models.AppBskyNotificationGetUnreadCount.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.notification.getUnreadCount', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationGetUnreadCount.Response)

    def list_notifications(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyNotificationListNotifications.Params,
                models.AppBskyNotificationListNotifications.ParamsDict,
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyNotificationListNotifications.Response':
        """Enumerate notifications for the requesting account. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationListNotifications.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyNotificationListNotifications.Params',
            get_or_create(params, models.AppBskyNotificationListNotifications.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.notification.listNotifications', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationListNotifications.Response)

    def put_preferences(
        self,
        data: t.Union[models.AppBskyNotificationPutPreferences.Data, models.AppBskyNotificationPutPreferences.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Set notification-related preferences for an account. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyNotificationPutPreferences.Data',
            get_or_create(data, models.AppBskyNotificationPutPreferences.Data),
        )
        response = self._client.invoke_procedure(
            'app.bsky.notification.putPreferences', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def register_push(
        self,
        data: t.Union[models.AppBskyNotificationRegisterPush.Data, models.AppBskyNotificationRegisterPush.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Register to receive push notifications, via a specified service, for the requesting account. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyNotificationRegisterPush.Data',
            get_or_create(data, models.AppBskyNotificationRegisterPush.Data),
        )
        response = self._client.invoke_procedure(
            'app.bsky.notification.registerPush', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_seen(
        self,
        data: t.Union[models.AppBskyNotificationUpdateSeen.Data, models.AppBskyNotificationUpdateSeen.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Notify server that the requesting account has seen notifications. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.AppBskyNotificationUpdateSeen.Data', get_or_create(data, models.AppBskyNotificationUpdateSeen.Data)
        )
        response = self._client.invoke_procedure(
            'app.bsky.notification.updateSeen', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AppBskyUnspeccedNamespace(NamespaceBase):
    def get_config(self, **kwargs: t.Any) -> 'models.AppBskyUnspeccedGetConfig.Response':
        """Get miscellaneous runtime configuration.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetConfig.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'app.bsky.unspecced.getConfig', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetConfig.Response)

    def get_popular_feed_generators(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyUnspeccedGetPopularFeedGenerators.Params,
                models.AppBskyUnspeccedGetPopularFeedGenerators.ParamsDict,
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedGetPopularFeedGenerators.Response':
        """An unspecced view of globally popular feed generators.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetPopularFeedGenerators.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedGetPopularFeedGenerators.Params',
            get_or_create(params, models.AppBskyUnspeccedGetPopularFeedGenerators.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.getPopularFeedGenerators',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyUnspeccedGetPopularFeedGenerators.Response)

    def get_suggestions_skeleton(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyUnspeccedGetSuggestionsSkeleton.Params,
                models.AppBskyUnspeccedGetSuggestionsSkeleton.ParamsDict,
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedGetSuggestionsSkeleton.Response':
        """Get a skeleton of suggested actors. Intended to be called and then hydrated through app.bsky.actor.getSuggestions.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetSuggestionsSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedGetSuggestionsSkeleton.Params',
            get_or_create(params, models.AppBskyUnspeccedGetSuggestionsSkeleton.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.getSuggestionsSkeleton',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyUnspeccedGetSuggestionsSkeleton.Response)

    def get_tagged_suggestions(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyUnspeccedGetTaggedSuggestions.Params,
                models.AppBskyUnspeccedGetTaggedSuggestions.ParamsDict,
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedGetTaggedSuggestions.Response':
        """Get a list of suggestions (feeds and users) tagged with categories.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetTaggedSuggestions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedGetTaggedSuggestions.Params',
            get_or_create(params, models.AppBskyUnspeccedGetTaggedSuggestions.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.getTaggedSuggestions', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetTaggedSuggestions.Response)

    def get_trending_topics(
        self,
        params: t.Optional[
            t.Union[
                models.AppBskyUnspeccedGetTrendingTopics.Params, models.AppBskyUnspeccedGetTrendingTopics.ParamsDict
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedGetTrendingTopics.Response':
        """Get a list of trending topics.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetTrendingTopics.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedGetTrendingTopics.Params',
            get_or_create(params, models.AppBskyUnspeccedGetTrendingTopics.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.getTrendingTopics', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetTrendingTopics.Response)

    def search_actors_skeleton(
        self,
        params: t.Union[
            models.AppBskyUnspeccedSearchActorsSkeleton.Params, models.AppBskyUnspeccedSearchActorsSkeleton.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedSearchActorsSkeleton.Response':
        """Backend Actors (profile) search, returns only skeleton.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedSearchActorsSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedSearchActorsSkeleton.Params',
            get_or_create(params, models.AppBskyUnspeccedSearchActorsSkeleton.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.searchActorsSkeleton', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedSearchActorsSkeleton.Response)

    def search_posts_skeleton(
        self,
        params: t.Union[
            models.AppBskyUnspeccedSearchPostsSkeleton.Params, models.AppBskyUnspeccedSearchPostsSkeleton.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedSearchPostsSkeleton.Response':
        """Backend Posts search, returns only skeleton.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedSearchPostsSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedSearchPostsSkeleton.Params',
            get_or_create(params, models.AppBskyUnspeccedSearchPostsSkeleton.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.searchPostsSkeleton', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedSearchPostsSkeleton.Response)

    def search_starter_packs_skeleton(
        self,
        params: t.Union[
            models.AppBskyUnspeccedSearchStarterPacksSkeleton.Params,
            models.AppBskyUnspeccedSearchStarterPacksSkeleton.ParamsDict,
        ],
        **kwargs: t.Any,
    ) -> 'models.AppBskyUnspeccedSearchStarterPacksSkeleton.Response':
        """Backend Starter Pack search, returns only skeleton.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedSearchStarterPacksSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyUnspeccedSearchStarterPacksSkeleton.Params',
            get_or_create(params, models.AppBskyUnspeccedSearchStarterPacksSkeleton.Params),
        )
        response = self._client.invoke_query(
            'app.bsky.unspecced.searchStarterPacksSkeleton',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyUnspeccedSearchStarterPacksSkeleton.Response)


class AppBskyVideoNamespace(NamespaceBase):
    def get_job_status(
        self,
        params: t.Union[models.AppBskyVideoGetJobStatus.Params, models.AppBskyVideoGetJobStatus.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.AppBskyVideoGetJobStatus.Response':
        """Get status details for a video processing job.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyVideoGetJobStatus.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.AppBskyVideoGetJobStatus.Params', get_or_create(params, models.AppBskyVideoGetJobStatus.Params)
        )
        response = self._client.invoke_query(
            'app.bsky.video.getJobStatus', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyVideoGetJobStatus.Response)

    def get_upload_limits(self, **kwargs: t.Any) -> 'models.AppBskyVideoGetUploadLimits.Response':
        """Get video upload limits for the authenticated user.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyVideoGetUploadLimits.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'app.bsky.video.getUploadLimits', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyVideoGetUploadLimits.Response)

    def upload_video(
        self, data: 'models.AppBskyVideoUploadVideo.Data', **kwargs: t.Any
    ) -> 'models.AppBskyVideoUploadVideo.Response':
        """Upload a video to be processed then stored on the PDS.

        Args:
            data: Input data alias.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyVideoUploadVideo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'app.bsky.video.uploadVideo',
            data=data,
            input_encoding='video/mp4',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyVideoUploadVideo.Response)


class ChatNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.bsky = ChatBskyNamespace(self._client)


class ChatBskyNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.actor = ChatBskyActorNamespace(self._client)
        self.convo = ChatBskyConvoNamespace(self._client)
        self.moderation = ChatBskyModerationNamespace(self._client)


class ChatBskyActorDeclarationRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.ChatBskyActorDeclaration.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyActorDeclaration.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='chat.bsky.actor.declaration', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.ChatBskyActorDeclaration.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.ChatBskyActorDeclaration.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.ChatBskyActorDeclaration.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyActorDeclaration.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='chat.bsky.actor.declaration',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.ChatBskyActorDeclaration.ListRecordsResponse(
            records={
                record.uri: t.cast('models.ChatBskyActorDeclaration.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.ChatBskyActorDeclaration.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.ChatBskyActorDeclaration.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyActorDeclaration.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='chat.bsky.actor.declaration',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.ChatBskyActorDeclaration.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='chat.bsky.actor.declaration',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ChatBskyActorNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.declaration = ChatBskyActorDeclarationRecord(self._client)

    def delete_account(self, **kwargs: t.Any) -> 'models.ChatBskyActorDeleteAccount.Response':
        """Delete account.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyActorDeleteAccount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'chat.bsky.actor.deleteAccount', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyActorDeleteAccount.Response)

    def export_account_data(self, **kwargs: t.Any) -> 'models.ChatBskyActorExportAccountData.Response':
        """Export account data.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyActorExportAccountData.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'chat.bsky.actor.exportAccountData', output_encoding='application/jsonl', **kwargs
        )
        return get_response_model(response, models.ChatBskyActorExportAccountData.Response)


class ChatBskyConvoNamespace(NamespaceBase):
    def accept_convo(
        self,
        data: t.Union[models.ChatBskyConvoAcceptConvo.Data, models.ChatBskyConvoAcceptConvo.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoAcceptConvo.Response':
        """Accept convo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoAcceptConvo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoAcceptConvo.Data', get_or_create(data, models.ChatBskyConvoAcceptConvo.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.acceptConvo',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoAcceptConvo.Response)

    def delete_message_for_self(
        self,
        data: t.Union[models.ChatBskyConvoDeleteMessageForSelf.Data, models.ChatBskyConvoDeleteMessageForSelf.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoDefs.DeletedMessageView':
        """Delete message for self.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoDefs.DeletedMessageView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoDeleteMessageForSelf.Data',
            get_or_create(data, models.ChatBskyConvoDeleteMessageForSelf.Data),
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.deleteMessageForSelf',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoDefs.DeletedMessageView)

    def get_convo(
        self,
        params: t.Union[models.ChatBskyConvoGetConvo.Params, models.ChatBskyConvoGetConvo.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoGetConvo.Response':
        """Get convo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoGetConvo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoGetConvo.Params', get_or_create(params, models.ChatBskyConvoGetConvo.Params)
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.getConvo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoGetConvo.Response)

    def get_convo_availability(
        self,
        params: t.Union[
            models.ChatBskyConvoGetConvoAvailability.Params, models.ChatBskyConvoGetConvoAvailability.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoGetConvoAvailability.Response':
        """Get whether the requester and the other members can chat. If an existing convo is found for these members, it is returned.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoGetConvoAvailability.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoGetConvoAvailability.Params',
            get_or_create(params, models.ChatBskyConvoGetConvoAvailability.Params),
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.getConvoAvailability', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoGetConvoAvailability.Response)

    def get_convo_for_members(
        self,
        params: t.Union[
            models.ChatBskyConvoGetConvoForMembers.Params, models.ChatBskyConvoGetConvoForMembers.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoGetConvoForMembers.Response':
        """Get convo for members.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoGetConvoForMembers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoGetConvoForMembers.Params',
            get_or_create(params, models.ChatBskyConvoGetConvoForMembers.Params),
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.getConvoForMembers', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoGetConvoForMembers.Response)

    def get_log(
        self,
        params: t.Optional[t.Union[models.ChatBskyConvoGetLog.Params, models.ChatBskyConvoGetLog.ParamsDict]] = None,
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoGetLog.Response':
        """Get log.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoGetLog.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoGetLog.Params', get_or_create(params, models.ChatBskyConvoGetLog.Params)
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.getLog', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoGetLog.Response)

    def get_messages(
        self,
        params: t.Union[models.ChatBskyConvoGetMessages.Params, models.ChatBskyConvoGetMessages.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoGetMessages.Response':
        """Get messages.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoGetMessages.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoGetMessages.Params', get_or_create(params, models.ChatBskyConvoGetMessages.Params)
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.getMessages', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoGetMessages.Response)

    def leave_convo(
        self,
        data: t.Union[models.ChatBskyConvoLeaveConvo.Data, models.ChatBskyConvoLeaveConvo.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoLeaveConvo.Response':
        """Leave convo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoLeaveConvo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoLeaveConvo.Data', get_or_create(data, models.ChatBskyConvoLeaveConvo.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.leaveConvo',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoLeaveConvo.Response)

    def list_convos(
        self,
        params: t.Optional[
            t.Union[models.ChatBskyConvoListConvos.Params, models.ChatBskyConvoListConvos.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoListConvos.Response':
        """List convos.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoListConvos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyConvoListConvos.Params', get_or_create(params, models.ChatBskyConvoListConvos.Params)
        )
        response = self._client.invoke_query(
            'chat.bsky.convo.listConvos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyConvoListConvos.Response)

    def mute_convo(
        self, data: t.Union[models.ChatBskyConvoMuteConvo.Data, models.ChatBskyConvoMuteConvo.DataDict], **kwargs: t.Any
    ) -> 'models.ChatBskyConvoMuteConvo.Response':
        """Mute convo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoMuteConvo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoMuteConvo.Data', get_or_create(data, models.ChatBskyConvoMuteConvo.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.muteConvo',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoMuteConvo.Response)

    def send_message(
        self,
        data: t.Union[models.ChatBskyConvoSendMessage.Data, models.ChatBskyConvoSendMessage.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoDefs.MessageView':
        """Send message.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoDefs.MessageView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoSendMessage.Data', get_or_create(data, models.ChatBskyConvoSendMessage.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.sendMessage',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoDefs.MessageView)

    def send_message_batch(
        self,
        data: t.Union[models.ChatBskyConvoSendMessageBatch.Data, models.ChatBskyConvoSendMessageBatch.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoSendMessageBatch.Response':
        """Send message batch.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoSendMessageBatch.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoSendMessageBatch.Data', get_or_create(data, models.ChatBskyConvoSendMessageBatch.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.sendMessageBatch',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoSendMessageBatch.Response)

    def unmute_convo(
        self,
        data: t.Union[models.ChatBskyConvoUnmuteConvo.Data, models.ChatBskyConvoUnmuteConvo.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoUnmuteConvo.Response':
        """Unmute convo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoUnmuteConvo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoUnmuteConvo.Data', get_or_create(data, models.ChatBskyConvoUnmuteConvo.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.unmuteConvo',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoUnmuteConvo.Response)

    def update_all_read(
        self,
        data: t.Optional[
            t.Union[models.ChatBskyConvoUpdateAllRead.Data, models.ChatBskyConvoUpdateAllRead.DataDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoUpdateAllRead.Response':
        """Update all read.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoUpdateAllRead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoUpdateAllRead.Data', get_or_create(data, models.ChatBskyConvoUpdateAllRead.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.updateAllRead',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoUpdateAllRead.Response)

    def update_read(
        self,
        data: t.Union[models.ChatBskyConvoUpdateRead.Data, models.ChatBskyConvoUpdateRead.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyConvoUpdateRead.Response':
        """Update read.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyConvoUpdateRead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyConvoUpdateRead.Data', get_or_create(data, models.ChatBskyConvoUpdateRead.Data)
        )
        response = self._client.invoke_procedure(
            'chat.bsky.convo.updateRead',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ChatBskyConvoUpdateRead.Response)


class ChatBskyModerationNamespace(NamespaceBase):
    def get_actor_metadata(
        self,
        params: t.Union[
            models.ChatBskyModerationGetActorMetadata.Params, models.ChatBskyModerationGetActorMetadata.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyModerationGetActorMetadata.Response':
        """Get actor metadata.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyModerationGetActorMetadata.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyModerationGetActorMetadata.Params',
            get_or_create(params, models.ChatBskyModerationGetActorMetadata.Params),
        )
        response = self._client.invoke_query(
            'chat.bsky.moderation.getActorMetadata', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyModerationGetActorMetadata.Response)

    def get_message_context(
        self,
        params: t.Union[
            models.ChatBskyModerationGetMessageContext.Params, models.ChatBskyModerationGetMessageContext.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ChatBskyModerationGetMessageContext.Response':
        """Get message context.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ChatBskyModerationGetMessageContext.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ChatBskyModerationGetMessageContext.Params',
            get_or_create(params, models.ChatBskyModerationGetMessageContext.Params),
        )
        response = self._client.invoke_query(
            'chat.bsky.moderation.getMessageContext', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ChatBskyModerationGetMessageContext.Response)

    def update_actor_access(
        self,
        data: t.Union[
            models.ChatBskyModerationUpdateActorAccess.Data, models.ChatBskyModerationUpdateActorAccess.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Update actor access.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ChatBskyModerationUpdateActorAccess.Data',
            get_or_create(data, models.ChatBskyModerationUpdateActorAccess.Data),
        )
        response = self._client.invoke_procedure(
            'chat.bsky.moderation.updateActorAccess', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.atproto = ComAtprotoNamespace(self._client)


class ComAtprotoNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.admin = ComAtprotoAdminNamespace(self._client)
        self.identity = ComAtprotoIdentityNamespace(self._client)
        self.label = ComAtprotoLabelNamespace(self._client)
        self.lexicon = ComAtprotoLexiconNamespace(self._client)
        self.moderation = ComAtprotoModerationNamespace(self._client)
        self.repo = ComAtprotoRepoNamespace(self._client)
        self.server = ComAtprotoServerNamespace(self._client)
        self.sync = ComAtprotoSyncNamespace(self._client)
        self.temp = ComAtprotoTempNamespace(self._client)


class ComAtprotoAdminNamespace(NamespaceBase):
    def delete_account(
        self,
        data: t.Union[models.ComAtprotoAdminDeleteAccount.Data, models.ComAtprotoAdminDeleteAccount.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Delete a user account as an administrator.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminDeleteAccount.Data', get_or_create(data, models.ComAtprotoAdminDeleteAccount.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.deleteAccount', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def disable_account_invites(
        self,
        data: t.Union[
            models.ComAtprotoAdminDisableAccountInvites.Data, models.ComAtprotoAdminDisableAccountInvites.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Disable an account from receiving new invite codes, but does not invalidate existing codes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminDisableAccountInvites.Data',
            get_or_create(data, models.ComAtprotoAdminDisableAccountInvites.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.disableAccountInvites', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def disable_invite_codes(
        self,
        data: t.Optional[
            t.Union[models.ComAtprotoAdminDisableInviteCodes.Data, models.ComAtprotoAdminDisableInviteCodes.DataDict]
        ] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Disable some set of codes and/or all codes associated with a set of users.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminDisableInviteCodes.Data',
            get_or_create(data, models.ComAtprotoAdminDisableInviteCodes.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.disableInviteCodes', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def enable_account_invites(
        self,
        data: t.Union[
            models.ComAtprotoAdminEnableAccountInvites.Data, models.ComAtprotoAdminEnableAccountInvites.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Re-enable an account's ability to receive invite codes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminEnableAccountInvites.Data',
            get_or_create(data, models.ComAtprotoAdminEnableAccountInvites.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.enableAccountInvites', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def get_account_info(
        self,
        params: t.Union[models.ComAtprotoAdminGetAccountInfo.Params, models.ComAtprotoAdminGetAccountInfo.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminDefs.AccountView':
        """Get details about an account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminDefs.AccountView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoAdminGetAccountInfo.Params',
            get_or_create(params, models.ComAtprotoAdminGetAccountInfo.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.admin.getAccountInfo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminDefs.AccountView)

    def get_account_infos(
        self,
        params: t.Union[models.ComAtprotoAdminGetAccountInfos.Params, models.ComAtprotoAdminGetAccountInfos.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminGetAccountInfos.Response':
        """Get details about some accounts.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetAccountInfos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoAdminGetAccountInfos.Params',
            get_or_create(params, models.ComAtprotoAdminGetAccountInfos.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.admin.getAccountInfos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetAccountInfos.Response)

    def get_invite_codes(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoAdminGetInviteCodes.Params, models.ComAtprotoAdminGetInviteCodes.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminGetInviteCodes.Response':
        """Get an admin view of invite codes.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoAdminGetInviteCodes.Params',
            get_or_create(params, models.ComAtprotoAdminGetInviteCodes.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.admin.getInviteCodes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetInviteCodes.Response)

    def get_subject_status(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoAdminGetSubjectStatus.Params, models.ComAtprotoAdminGetSubjectStatus.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminGetSubjectStatus.Response':
        """Get the service-specific admin status of a subject (account, record, or blob).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetSubjectStatus.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoAdminGetSubjectStatus.Params',
            get_or_create(params, models.ComAtprotoAdminGetSubjectStatus.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.admin.getSubjectStatus', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetSubjectStatus.Response)

    def search_accounts(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoAdminSearchAccounts.Params, models.ComAtprotoAdminSearchAccounts.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminSearchAccounts.Response':
        """Get list of accounts that matches your search query.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminSearchAccounts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoAdminSearchAccounts.Params',
            get_or_create(params, models.ComAtprotoAdminSearchAccounts.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.admin.searchAccounts', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminSearchAccounts.Response)

    def send_email(
        self,
        data: t.Union[models.ComAtprotoAdminSendEmail.Data, models.ComAtprotoAdminSendEmail.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminSendEmail.Response':
        """Send email to a user's account email address.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminSendEmail.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminSendEmail.Data', get_or_create(data, models.ComAtprotoAdminSendEmail.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.sendEmail',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminSendEmail.Response)

    def update_account_email(
        self,
        data: t.Union[models.ComAtprotoAdminUpdateAccountEmail.Data, models.ComAtprotoAdminUpdateAccountEmail.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Administrative action to update an account's email.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminUpdateAccountEmail.Data',
            get_or_create(data, models.ComAtprotoAdminUpdateAccountEmail.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateAccountEmail', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_account_handle(
        self,
        data: t.Union[
            models.ComAtprotoAdminUpdateAccountHandle.Data, models.ComAtprotoAdminUpdateAccountHandle.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Administrative action to update an account's handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminUpdateAccountHandle.Data',
            get_or_create(data, models.ComAtprotoAdminUpdateAccountHandle.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateAccountHandle', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_account_password(
        self,
        data: t.Union[
            models.ComAtprotoAdminUpdateAccountPassword.Data, models.ComAtprotoAdminUpdateAccountPassword.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Update the password for a user account as an administrator.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminUpdateAccountPassword.Data',
            get_or_create(data, models.ComAtprotoAdminUpdateAccountPassword.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateAccountPassword', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_subject_status(
        self,
        data: t.Union[
            models.ComAtprotoAdminUpdateSubjectStatus.Data, models.ComAtprotoAdminUpdateSubjectStatus.DataDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoAdminUpdateSubjectStatus.Response':
        """Update the service-specific admin status of a subject (account, record, or blob).

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminUpdateSubjectStatus.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoAdminUpdateSubjectStatus.Data',
            get_or_create(data, models.ComAtprotoAdminUpdateSubjectStatus.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateSubjectStatus',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminUpdateSubjectStatus.Response)


class ComAtprotoIdentityNamespace(NamespaceBase):
    def get_recommended_did_credentials(
        self, **kwargs: t.Any
    ) -> 'models.ComAtprotoIdentityGetRecommendedDidCredentials.Response':
        """Describe the credentials that should be included in the DID doc of an account that is migrating to this service.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityGetRecommendedDidCredentials.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.identity.getRecommendedDidCredentials', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityGetRecommendedDidCredentials.Response)

    def refresh_identity(
        self,
        data: t.Union[models.ComAtprotoIdentityRefreshIdentity.Data, models.ComAtprotoIdentityRefreshIdentity.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoIdentityDefs.IdentityInfo':
        """Request that the server re-resolve an identity (DID and handle). The server may ignore this request, or require authentication, depending on the role, implementation, and policy of the server.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityDefs.IdentityInfo`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoIdentityRefreshIdentity.Data',
            get_or_create(data, models.ComAtprotoIdentityRefreshIdentity.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.identity.refreshIdentity',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoIdentityDefs.IdentityInfo)

    def request_plc_operation_signature(self, **kwargs: t.Any) -> bool:
        """Request an email with a code to in order to request a signed PLC operation. Requires Auth.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure('com.atproto.identity.requestPlcOperationSignature', **kwargs)
        return get_response_model(response, bool)

    def resolve_did(
        self,
        params: t.Union[models.ComAtprotoIdentityResolveDid.Params, models.ComAtprotoIdentityResolveDid.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoIdentityResolveDid.Response':
        """Resolves DID to DID document. Does not bi-directionally verify handle.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityResolveDid.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoIdentityResolveDid.Params',
            get_or_create(params, models.ComAtprotoIdentityResolveDid.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.identity.resolveDid', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityResolveDid.Response)

    def resolve_handle(
        self,
        params: t.Union[
            models.ComAtprotoIdentityResolveHandle.Params, models.ComAtprotoIdentityResolveHandle.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoIdentityResolveHandle.Response':
        """Resolves an atproto handle (hostname) to a DID. Does not necessarily bi-directionally verify against the the DID document.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityResolveHandle.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoIdentityResolveHandle.Params',
            get_or_create(params, models.ComAtprotoIdentityResolveHandle.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.identity.resolveHandle', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityResolveHandle.Response)

    def resolve_identity(
        self,
        params: t.Union[
            models.ComAtprotoIdentityResolveIdentity.Params, models.ComAtprotoIdentityResolveIdentity.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoIdentityDefs.IdentityInfo':
        """Resolves an identity (DID or Handle) to a full identity (DID document and verified handle).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityDefs.IdentityInfo`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoIdentityResolveIdentity.Params',
            get_or_create(params, models.ComAtprotoIdentityResolveIdentity.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.identity.resolveIdentity', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityDefs.IdentityInfo)

    def sign_plc_operation(
        self,
        data: t.Optional[
            t.Union[models.ComAtprotoIdentitySignPlcOperation.Data, models.ComAtprotoIdentitySignPlcOperation.DataDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoIdentitySignPlcOperation.Response':
        """Signs a PLC operation to update some value(s) in the requesting DID's document.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentitySignPlcOperation.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoIdentitySignPlcOperation.Data',
            get_or_create(data, models.ComAtprotoIdentitySignPlcOperation.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.identity.signPlcOperation',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoIdentitySignPlcOperation.Response)

    def submit_plc_operation(
        self,
        data: t.Union[
            models.ComAtprotoIdentitySubmitPlcOperation.Data, models.ComAtprotoIdentitySubmitPlcOperation.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Validates a PLC operation to ensure that it doesn't violate a service's constraints or get the identity into a bad state, then submits it to the PLC registry.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoIdentitySubmitPlcOperation.Data',
            get_or_create(data, models.ComAtprotoIdentitySubmitPlcOperation.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.identity.submitPlcOperation', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_handle(
        self,
        data: t.Union[models.ComAtprotoIdentityUpdateHandle.Data, models.ComAtprotoIdentityUpdateHandle.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Updates the current account's handle. Verifies handle validity, and updates did:plc document if necessary. Implemented by PDS, and requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoIdentityUpdateHandle.Data',
            get_or_create(data, models.ComAtprotoIdentityUpdateHandle.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.identity.updateHandle', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComAtprotoLabelNamespace(NamespaceBase):
    def query_labels(
        self,
        params: t.Union[models.ComAtprotoLabelQueryLabels.Params, models.ComAtprotoLabelQueryLabels.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoLabelQueryLabels.Response':
        """Find labels relevant to the provided AT-URI patterns. Public endpoint for moderation services, though may return different or additional results with auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLabelQueryLabels.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoLabelQueryLabels.Params', get_or_create(params, models.ComAtprotoLabelQueryLabels.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.label.queryLabels', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoLabelQueryLabels.Response)


class ComAtprotoLexiconSchemaRecord(RecordBase):
    def get(
        self, repo: str, rkey: str, cid: t.Optional[str] = None, **kwargs: t.Any
    ) -> 'models.ComAtprotoLexiconSchema.GetRecordResponse':
        """Get a record.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            cid: The CID of the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLexiconSchema.GetRecordResponse`: Get record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoGetRecord.Params(
            collection='com.atproto.lexicon.schema', repo=repo, rkey=rkey, cid=cid
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoGetRecord.Response)
        return models.ComAtprotoLexiconSchema.GetRecordResponse(
            uri=response_model.uri,
            cid=response_model.cid,
            value=t.cast('models.ComAtprotoLexiconSchema.Record', response_model.value),
        )

    def list(
        self,
        repo: str,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
        reverse: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoLexiconSchema.ListRecordsResponse':
        """List a range of records in a collection.

        Args:
            repo: The repository (DID).
            cursor: The cursor.
            limit: The limit.
            reverse: Whether to reverse the order.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLexiconSchema.ListRecordsResponse`: List records response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = models.ComAtprotoRepoListRecords.Params(
            collection='com.atproto.lexicon.schema',
            repo=repo,
            cursor=cursor,
            limit=limit,
            reverse=reverse,
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        response_model = get_response_model(response, models.ComAtprotoRepoListRecords.Response)
        return models.ComAtprotoLexiconSchema.ListRecordsResponse(
            records={
                record.uri: t.cast('models.ComAtprotoLexiconSchema.Record', record.value)
                for record in response_model.records
            },
            cursor=response_model.cursor,
        )

    def create(
        self,
        repo: str,
        record: 'models.ComAtprotoLexiconSchema.Record',
        rkey: t.Optional[str] = None,
        swap_commit: t.Optional[str] = None,
        validate: t.Optional[bool] = True,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoLexiconSchema.CreateRecordResponse':
        """Create a new record.

        Args:
            repo: The repository (DID).
            record: The record.
            rkey: The record key (TID).
            swap_commit: The swap commit.
            validate: Whether to validate the record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLexiconSchema.CreateRecordResponse`: Create record response.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoCreateRecord.Data(
            collection='com.atproto.lexicon.schema',
            repo=repo,
            record=record,
            rkey=rkey,
            swap_commit=swap_commit,
            validate_=validate,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        response_model = get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)
        return models.ComAtprotoLexiconSchema.CreateRecordResponse(uri=response_model.uri, cid=response_model.cid)

    def delete(
        self,
        repo: str,
        rkey: str,
        swap_commit: t.Optional[str] = None,
        swap_record: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            repo: The repository (DID).
            rkey: The record key (TID).
            swap_commit: The swap commit.
            swap_record: The swap record.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = models.ComAtprotoRepoDeleteRecord.Data(
            collection='com.atproto.lexicon.schema',
            repo=repo,
            rkey=rkey,
            swap_commit=swap_commit,
            swap_record=swap_record,
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComAtprotoLexiconNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.schema = ComAtprotoLexiconSchemaRecord(self._client)


class ComAtprotoModerationNamespace(NamespaceBase):
    def create_report(
        self,
        data: t.Union[models.ComAtprotoModerationCreateReport.Data, models.ComAtprotoModerationCreateReport.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoModerationCreateReport.Response':
        """Submit a moderation report regarding an atproto account or record. Implemented by moderation services (with PDS proxying), and requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoModerationCreateReport.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoModerationCreateReport.Data',
            get_or_create(data, models.ComAtprotoModerationCreateReport.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.moderation.createReport',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoModerationCreateReport.Response)


class ComAtprotoRepoNamespace(NamespaceBase):
    def apply_writes(
        self,
        data: t.Union[models.ComAtprotoRepoApplyWrites.Data, models.ComAtprotoRepoApplyWrites.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoApplyWrites.Response':
        """Apply a batch transaction of repository creates, updates, and deletes. Requires auth, implemented by PDS.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoApplyWrites.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoRepoApplyWrites.Data', get_or_create(data, models.ComAtprotoRepoApplyWrites.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.applyWrites',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoApplyWrites.Response)

    def create_record(
        self,
        data: t.Union[models.ComAtprotoRepoCreateRecord.Data, models.ComAtprotoRepoCreateRecord.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoCreateRecord.Response':
        """Create a single new repository record. Requires auth, implemented by PDS.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoRepoCreateRecord.Data', get_or_create(data, models.ComAtprotoRepoCreateRecord.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)

    def delete_record(
        self,
        data: t.Union[models.ComAtprotoRepoDeleteRecord.Data, models.ComAtprotoRepoDeleteRecord.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoDeleteRecord.Response':
        """Delete a repository record, or ensure it doesn't exist. Requires auth, implemented by PDS.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoDeleteRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoRepoDeleteRecord.Data', get_or_create(data, models.ComAtprotoRepoDeleteRecord.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoDeleteRecord.Response)

    def describe_repo(
        self,
        params: t.Union[models.ComAtprotoRepoDescribeRepo.Params, models.ComAtprotoRepoDescribeRepo.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoDescribeRepo.Response':
        """Get information about an account and repository, including the list of collections. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoDescribeRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoRepoDescribeRepo.Params', get_or_create(params, models.ComAtprotoRepoDescribeRepo.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.repo.describeRepo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoDescribeRepo.Response)

    def get_record(
        self,
        params: t.Union[models.ComAtprotoRepoGetRecord.Params, models.ComAtprotoRepoGetRecord.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoGetRecord.Response':
        """Get a single record from a repository. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoRepoGetRecord.Params', get_or_create(params, models.ComAtprotoRepoGetRecord.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoGetRecord.Response)

    def import_repo(self, data: 'models.ComAtprotoRepoImportRepo.Data', **kwargs: t.Any) -> bool:
        """Import a repo in the form of a CAR file. Requires Content-Length HTTP header to be set.

        Args:
            data: Input data alias.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'com.atproto.repo.importRepo', data=data, input_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, bool)

    def list_missing_blobs(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoRepoListMissingBlobs.Params, models.ComAtprotoRepoListMissingBlobs.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoListMissingBlobs.Response':
        """Returns a list of missing blobs for the requesting account. Intended to be used in the account migration flow.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoListMissingBlobs.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoRepoListMissingBlobs.Params',
            get_or_create(params, models.ComAtprotoRepoListMissingBlobs.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listMissingBlobs', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoListMissingBlobs.Response)

    def list_records(
        self,
        params: t.Union[models.ComAtprotoRepoListRecords.Params, models.ComAtprotoRepoListRecords.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoListRecords.Response':
        """List a range of records in a repository, matching a specific collection. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoListRecords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoRepoListRecords.Params', get_or_create(params, models.ComAtprotoRepoListRecords.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoListRecords.Response)

    def put_record(
        self,
        data: t.Union[models.ComAtprotoRepoPutRecord.Data, models.ComAtprotoRepoPutRecord.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoRepoPutRecord.Response':
        """Write a repository record, creating or updating it as needed. Requires auth, implemented by PDS.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoPutRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoRepoPutRecord.Data', get_or_create(data, models.ComAtprotoRepoPutRecord.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.repo.putRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoPutRecord.Response)

    def upload_blob(
        self, data: 'models.ComAtprotoRepoUploadBlob.Data', **kwargs: t.Any
    ) -> 'models.ComAtprotoRepoUploadBlob.Response':
        """Upload a new blob, to be referenced from a repository record. The blob will be deleted if it is not referenced within a time window (eg, minutes). Blob restrictions (mimetype, size, etc) are enforced when the reference is created. Requires auth, implemented by PDS.

        Args:
            data: Input data alias.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoUploadBlob.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'com.atproto.repo.uploadBlob', data=data, input_encoding='*/*', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoUploadBlob.Response)


class ComAtprotoServerNamespace(NamespaceBase):
    def activate_account(self, **kwargs: t.Any) -> bool:
        """Activates a currently deactivated account. Used to finalize account migration after the account's repo is imported and identity is setup.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure('com.atproto.server.activateAccount', **kwargs)
        return get_response_model(response, bool)

    def check_account_status(self, **kwargs: t.Any) -> 'models.ComAtprotoServerCheckAccountStatus.Response':
        """Returns the status of an account, especially as pertaining to import or recovery. Can be called many times over the course of an account migration. Requires auth and can only be called pertaining to oneself.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCheckAccountStatus.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.server.checkAccountStatus', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerCheckAccountStatus.Response)

    def confirm_email(
        self,
        data: t.Union[models.ComAtprotoServerConfirmEmail.Data, models.ComAtprotoServerConfirmEmail.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Confirm an email using a token from com.atproto.server.requestEmailConfirmation.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerConfirmEmail.Data', get_or_create(data, models.ComAtprotoServerConfirmEmail.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.confirmEmail', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def create_account(
        self,
        data: t.Union[models.ComAtprotoServerCreateAccount.Data, models.ComAtprotoServerCreateAccount.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerCreateAccount.Response':
        """Create an account. Implemented by PDS.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAccount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerCreateAccount.Data', get_or_create(data, models.ComAtprotoServerCreateAccount.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.createAccount',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAccount.Response)

    def create_app_password(
        self,
        data: t.Union[models.ComAtprotoServerCreateAppPassword.Data, models.ComAtprotoServerCreateAppPassword.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerCreateAppPassword.AppPassword':
        """Create an App Password.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAppPassword.AppPassword`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerCreateAppPassword.Data',
            get_or_create(data, models.ComAtprotoServerCreateAppPassword.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.createAppPassword',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAppPassword.AppPassword)

    def create_invite_code(
        self,
        data: t.Union[models.ComAtprotoServerCreateInviteCode.Data, models.ComAtprotoServerCreateInviteCode.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerCreateInviteCode.Response':
        """Create an invite code.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateInviteCode.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerCreateInviteCode.Data',
            get_or_create(data, models.ComAtprotoServerCreateInviteCode.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.createInviteCode',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCode.Response)

    def create_invite_codes(
        self,
        data: t.Union[models.ComAtprotoServerCreateInviteCodes.Data, models.ComAtprotoServerCreateInviteCodes.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerCreateInviteCodes.Response':
        """Create invite codes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerCreateInviteCodes.Data',
            get_or_create(data, models.ComAtprotoServerCreateInviteCodes.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.createInviteCodes',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCodes.Response)

    def create_session(
        self,
        data: t.Union[models.ComAtprotoServerCreateSession.Data, models.ComAtprotoServerCreateSession.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerCreateSession.Response':
        """Create an authentication session.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerCreateSession.Data', get_or_create(data, models.ComAtprotoServerCreateSession.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.createSession',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateSession.Response)

    def deactivate_account(
        self,
        data: t.Optional[
            t.Union[models.ComAtprotoServerDeactivateAccount.Data, models.ComAtprotoServerDeactivateAccount.DataDict]
        ] = None,
        **kwargs: t.Any,
    ) -> bool:
        """Deactivates a currently active account. Stops serving of repo, and future writes to repo until reactivated. Used to finalize account migration with the old host after the account has been activated on the new host.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerDeactivateAccount.Data',
            get_or_create(data, models.ComAtprotoServerDeactivateAccount.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.deactivateAccount', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def delete_account(
        self,
        data: t.Union[models.ComAtprotoServerDeleteAccount.Data, models.ComAtprotoServerDeleteAccount.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Delete an actor's account with a token and password. Can only be called after requesting a deletion token. Requires auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerDeleteAccount.Data', get_or_create(data, models.ComAtprotoServerDeleteAccount.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.deleteAccount', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def delete_session(self, **kwargs: t.Any) -> bool:
        """Delete the current session. Requires auth.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure('com.atproto.server.deleteSession', **kwargs)
        return get_response_model(response, bool)

    def describe_server(self, **kwargs: t.Any) -> 'models.ComAtprotoServerDescribeServer.Response':
        """Describes the server's account creation requirements and capabilities. Implemented by PDS.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerDescribeServer.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.server.describeServer', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerDescribeServer.Response)

    def get_account_invite_codes(
        self,
        params: t.Optional[
            t.Union[
                models.ComAtprotoServerGetAccountInviteCodes.Params,
                models.ComAtprotoServerGetAccountInviteCodes.ParamsDict,
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerGetAccountInviteCodes.Response':
        """Get all invite codes for the current account. Requires auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetAccountInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoServerGetAccountInviteCodes.Params',
            get_or_create(params, models.ComAtprotoServerGetAccountInviteCodes.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.server.getAccountInviteCodes',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerGetAccountInviteCodes.Response)

    def get_service_auth(
        self,
        params: t.Union[models.ComAtprotoServerGetServiceAuth.Params, models.ComAtprotoServerGetServiceAuth.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerGetServiceAuth.Response':
        """Get a signed token on behalf of the requesting DID for the requested service.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetServiceAuth.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoServerGetServiceAuth.Params',
            get_or_create(params, models.ComAtprotoServerGetServiceAuth.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.server.getServiceAuth', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerGetServiceAuth.Response)

    def get_session(self, **kwargs: t.Any) -> 'models.ComAtprotoServerGetSession.Response':
        """Get information about the current auth session. Requires auth.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.server.getSession', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerGetSession.Response)

    def list_app_passwords(self, **kwargs: t.Any) -> 'models.ComAtprotoServerListAppPasswords.Response':
        """List all App Passwords.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerListAppPasswords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.server.listAppPasswords', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerListAppPasswords.Response)

    def refresh_session(self, **kwargs: t.Any) -> 'models.ComAtprotoServerRefreshSession.Response':
        """Refresh an authentication session. Requires auth using the 'refreshJwt' (not the 'accessJwt').

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerRefreshSession.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'com.atproto.server.refreshSession', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerRefreshSession.Response)

    def request_account_delete(self, **kwargs: t.Any) -> bool:
        """Initiate a user account deletion via email.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure('com.atproto.server.requestAccountDelete', **kwargs)
        return get_response_model(response, bool)

    def request_email_confirmation(self, **kwargs: t.Any) -> bool:
        """Request an email with a code to confirm ownership of email.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure('com.atproto.server.requestEmailConfirmation', **kwargs)
        return get_response_model(response, bool)

    def request_email_update(self, **kwargs: t.Any) -> 'models.ComAtprotoServerRequestEmailUpdate.Response':
        """Request a token in order to update email.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerRequestEmailUpdate.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_procedure(
            'com.atproto.server.requestEmailUpdate', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoServerRequestEmailUpdate.Response)

    def request_password_reset(
        self,
        data: t.Union[
            models.ComAtprotoServerRequestPasswordReset.Data, models.ComAtprotoServerRequestPasswordReset.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Initiate a user account password reset via email.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerRequestPasswordReset.Data',
            get_or_create(data, models.ComAtprotoServerRequestPasswordReset.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.requestPasswordReset', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def reserve_signing_key(
        self,
        data: t.Optional[
            t.Union[models.ComAtprotoServerReserveSigningKey.Data, models.ComAtprotoServerReserveSigningKey.DataDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoServerReserveSigningKey.Response':
        """Reserve a repo signing key, for use with account creation. Necessary so that a DID PLC update operation can be constructed during an account migraiton. Public and does not require auth; implemented by PDS. NOTE: this endpoint may change when full account migration is implemented.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerReserveSigningKey.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerReserveSigningKey.Data',
            get_or_create(data, models.ComAtprotoServerReserveSigningKey.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.reserveSigningKey',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerReserveSigningKey.Response)

    def reset_password(
        self,
        data: t.Union[models.ComAtprotoServerResetPassword.Data, models.ComAtprotoServerResetPassword.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Reset a user account password using a token.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerResetPassword.Data', get_or_create(data, models.ComAtprotoServerResetPassword.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.resetPassword', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def revoke_app_password(
        self,
        data: t.Union[models.ComAtprotoServerRevokeAppPassword.Data, models.ComAtprotoServerRevokeAppPassword.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Revoke an App Password by name.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerRevokeAppPassword.Data',
            get_or_create(data, models.ComAtprotoServerRevokeAppPassword.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.revokeAppPassword', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_email(
        self,
        data: t.Union[models.ComAtprotoServerUpdateEmail.Data, models.ComAtprotoServerUpdateEmail.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Update an account's email.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoServerUpdateEmail.Data', get_or_create(data, models.ComAtprotoServerUpdateEmail.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.server.updateEmail', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComAtprotoSyncNamespace(NamespaceBase):
    def get_blob(
        self,
        params: t.Union[models.ComAtprotoSyncGetBlob.Params, models.ComAtprotoSyncGetBlob.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetBlob.Response':
        """Get a blob associated with a given account. Returns the full blob as originally uploaded. Does not require auth; implemented by PDS.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlob.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetBlob.Params', get_or_create(params, models.ComAtprotoSyncGetBlob.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getBlob', params=params_model, output_encoding='*/*', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlob.Response)

    def get_blocks(
        self,
        params: t.Union[models.ComAtprotoSyncGetBlocks.Params, models.ComAtprotoSyncGetBlocks.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetBlocks.Response':
        """Get data blocks from a given repo, by CID. For example, intermediate MST nodes, or records. Does not require auth; implemented by PDS.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetBlocks.Params', get_or_create(params, models.ComAtprotoSyncGetBlocks.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getBlocks', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlocks.Response)

    def get_checkout(
        self,
        params: t.Union[models.ComAtprotoSyncGetCheckout.Params, models.ComAtprotoSyncGetCheckout.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetCheckout.Response':
        """DEPRECATED - please use com.atproto.sync.getRepo instead.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetCheckout.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetCheckout.Params', get_or_create(params, models.ComAtprotoSyncGetCheckout.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getCheckout', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetCheckout.Response)

    def get_head(
        self,
        params: t.Union[models.ComAtprotoSyncGetHead.Params, models.ComAtprotoSyncGetHead.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetHead.Response':
        """DEPRECATED - please use com.atproto.sync.getLatestCommit instead.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetHead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetHead.Params', get_or_create(params, models.ComAtprotoSyncGetHead.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getHead', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetHead.Response)

    def get_latest_commit(
        self,
        params: t.Union[models.ComAtprotoSyncGetLatestCommit.Params, models.ComAtprotoSyncGetLatestCommit.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetLatestCommit.Response':
        """Get the current commit CID & revision of the specified repo. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetLatestCommit.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetLatestCommit.Params',
            get_or_create(params, models.ComAtprotoSyncGetLatestCommit.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getLatestCommit', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetLatestCommit.Response)

    def get_record(
        self,
        params: t.Union[models.ComAtprotoSyncGetRecord.Params, models.ComAtprotoSyncGetRecord.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetRecord.Response':
        """Get data blocks needed to prove the existence or non-existence of record in the current version of repo. Does not require auth.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetRecord.Params', get_or_create(params, models.ComAtprotoSyncGetRecord.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getRecord', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRecord.Response)

    def get_repo(
        self,
        params: t.Union[models.ComAtprotoSyncGetRepo.Params, models.ComAtprotoSyncGetRepo.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetRepo.Response':
        """Download a repository export as CAR file. Optionally only a 'diff' since a previous revision. Does not require auth; implemented by PDS.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetRepo.Params', get_or_create(params, models.ComAtprotoSyncGetRepo.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getRepo', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRepo.Response)

    def get_repo_status(
        self,
        params: t.Union[models.ComAtprotoSyncGetRepoStatus.Params, models.ComAtprotoSyncGetRepoStatus.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncGetRepoStatus.Response':
        """Get the hosting status for a repository, on this server. Expected to be implemented by PDS and Relay.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRepoStatus.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncGetRepoStatus.Params',
            get_or_create(params, models.ComAtprotoSyncGetRepoStatus.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.sync.getRepoStatus', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRepoStatus.Response)

    def list_blobs(
        self,
        params: t.Union[models.ComAtprotoSyncListBlobs.Params, models.ComAtprotoSyncListBlobs.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncListBlobs.Response':
        """List blob CIDs for an account, since some repo revision. Does not require auth; implemented by PDS.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListBlobs.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncListBlobs.Params', get_or_create(params, models.ComAtprotoSyncListBlobs.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.listBlobs', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListBlobs.Response)

    def list_repos(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoSyncListRepos.Params, models.ComAtprotoSyncListRepos.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncListRepos.Response':
        """Enumerates all the DID, rev, and commit CID for all repos hosted by this service. Does not require auth; implemented by PDS and Relay.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncListRepos.Params', get_or_create(params, models.ComAtprotoSyncListRepos.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.sync.listRepos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListRepos.Response)

    def list_repos_by_collection(
        self,
        params: t.Union[
            models.ComAtprotoSyncListReposByCollection.Params, models.ComAtprotoSyncListReposByCollection.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoSyncListReposByCollection.Response':
        """Enumerates all the DIDs which have records with the given collection NSID.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListReposByCollection.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoSyncListReposByCollection.Params',
            get_or_create(params, models.ComAtprotoSyncListReposByCollection.Params),
        )
        response = self._client.invoke_query(
            'com.atproto.sync.listReposByCollection', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListReposByCollection.Response)

    def notify_of_update(
        self,
        data: t.Union[models.ComAtprotoSyncNotifyOfUpdate.Data, models.ComAtprotoSyncNotifyOfUpdate.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Notify a crawling service of a recent update, and that crawling should resume. Intended use is after a gap between repo stream events caused the crawling service to disconnect. Does not require auth; implemented by Relay. DEPRECATED: just use com.atproto.sync.requestCrawl.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoSyncNotifyOfUpdate.Data', get_or_create(data, models.ComAtprotoSyncNotifyOfUpdate.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.sync.notifyOfUpdate', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def request_crawl(
        self,
        data: t.Union[models.ComAtprotoSyncRequestCrawl.Data, models.ComAtprotoSyncRequestCrawl.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Request a service to persistently crawl hosted repos. Expected use is new PDS instances declaring their existence to Relays. Does not require auth.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoSyncRequestCrawl.Data', get_or_create(data, models.ComAtprotoSyncRequestCrawl.Data)
        )
        response = self._client.invoke_procedure(
            'com.atproto.sync.requestCrawl', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComAtprotoTempNamespace(NamespaceBase):
    def add_reserved_handle(
        self,
        data: t.Union[models.ComAtprotoTempAddReservedHandle.Data, models.ComAtprotoTempAddReservedHandle.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoTempAddReservedHandle.Response':
        """Add a handle to the set of reserved handles.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoTempAddReservedHandle.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoTempAddReservedHandle.Data',
            get_or_create(data, models.ComAtprotoTempAddReservedHandle.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.temp.addReservedHandle',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoTempAddReservedHandle.Response)

    def check_signup_queue(self, **kwargs: t.Any) -> 'models.ComAtprotoTempCheckSignupQueue.Response':
        """Check accounts location in signup queue.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoTempCheckSignupQueue.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'com.atproto.temp.checkSignupQueue', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoTempCheckSignupQueue.Response)

    def fetch_labels(
        self,
        params: t.Optional[
            t.Union[models.ComAtprotoTempFetchLabels.Params, models.ComAtprotoTempFetchLabels.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ComAtprotoTempFetchLabels.Response':
        """DEPRECATED: use queryLabels or subscribeLabels instead -- Fetch all labels from a labeler created after a certain date.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoTempFetchLabels.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ComAtprotoTempFetchLabels.Params', get_or_create(params, models.ComAtprotoTempFetchLabels.Params)
        )
        response = self._client.invoke_query(
            'com.atproto.temp.fetchLabels', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoTempFetchLabels.Response)

    def request_phone_verification(
        self,
        data: t.Union[
            models.ComAtprotoTempRequestPhoneVerification.Data, models.ComAtprotoTempRequestPhoneVerification.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Request a verification code to be sent to the supplied phone number.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ComAtprotoTempRequestPhoneVerification.Data',
            get_or_create(data, models.ComAtprotoTempRequestPhoneVerification.Data),
        )
        response = self._client.invoke_procedure(
            'com.atproto.temp.requestPhoneVerification', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ToolsNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.ozone = ToolsOzoneNamespace(self._client)


class ToolsOzoneNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.communication = ToolsOzoneCommunicationNamespace(self._client)
        self.moderation = ToolsOzoneModerationNamespace(self._client)
        self.server = ToolsOzoneServerNamespace(self._client)
        self.set = ToolsOzoneSetNamespace(self._client)
        self.setting = ToolsOzoneSettingNamespace(self._client)
        self.signature = ToolsOzoneSignatureNamespace(self._client)
        self.team = ToolsOzoneTeamNamespace(self._client)


class ToolsOzoneCommunicationNamespace(NamespaceBase):
    def create_template(
        self,
        data: t.Union[
            models.ToolsOzoneCommunicationCreateTemplate.Data, models.ToolsOzoneCommunicationCreateTemplate.DataDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneCommunicationDefs.TemplateView':
        """Administrative action to create a new, re-usable communication (email for now) template.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneCommunicationDefs.TemplateView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneCommunicationCreateTemplate.Data',
            get_or_create(data, models.ToolsOzoneCommunicationCreateTemplate.Data),
        )
        response = self._client.invoke_procedure(
            'tools.ozone.communication.createTemplate',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneCommunicationDefs.TemplateView)

    def delete_template(
        self,
        data: t.Union[
            models.ToolsOzoneCommunicationDeleteTemplate.Data, models.ToolsOzoneCommunicationDeleteTemplate.DataDict
        ],
        **kwargs: t.Any,
    ) -> bool:
        """Delete a communication template.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneCommunicationDeleteTemplate.Data',
            get_or_create(data, models.ToolsOzoneCommunicationDeleteTemplate.Data),
        )
        response = self._client.invoke_procedure(
            'tools.ozone.communication.deleteTemplate', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def list_templates(self, **kwargs: t.Any) -> 'models.ToolsOzoneCommunicationListTemplates.Response':
        """Get list of all communication templates.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneCommunicationListTemplates.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'tools.ozone.communication.listTemplates', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneCommunicationListTemplates.Response)

    def update_template(
        self,
        data: t.Union[
            models.ToolsOzoneCommunicationUpdateTemplate.Data, models.ToolsOzoneCommunicationUpdateTemplate.DataDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneCommunicationDefs.TemplateView':
        """Administrative action to update an existing communication template. Allows passing partial fields to patch specific fields only.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneCommunicationDefs.TemplateView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneCommunicationUpdateTemplate.Data',
            get_or_create(data, models.ToolsOzoneCommunicationUpdateTemplate.Data),
        )
        response = self._client.invoke_procedure(
            'tools.ozone.communication.updateTemplate',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneCommunicationDefs.TemplateView)


class ToolsOzoneModerationNamespace(NamespaceBase):
    def emit_event(
        self,
        data: t.Union[models.ToolsOzoneModerationEmitEvent.Data, models.ToolsOzoneModerationEmitEvent.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationDefs.ModEventView':
        """Take a moderation action on an actor.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationDefs.ModEventView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneModerationEmitEvent.Data', get_or_create(data, models.ToolsOzoneModerationEmitEvent.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.moderation.emitEvent',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneModerationDefs.ModEventView)

    def get_event(
        self,
        params: t.Union[models.ToolsOzoneModerationGetEvent.Params, models.ToolsOzoneModerationGetEvent.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationDefs.ModEventViewDetail':
        """Get details about a moderation event.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationDefs.ModEventViewDetail`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetEvent.Params',
            get_or_create(params, models.ToolsOzoneModerationGetEvent.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getEvent', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationDefs.ModEventViewDetail)

    def get_record(
        self,
        params: t.Union[models.ToolsOzoneModerationGetRecord.Params, models.ToolsOzoneModerationGetRecord.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationDefs.RecordViewDetail':
        """Get details about a record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationDefs.RecordViewDetail`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetRecord.Params',
            get_or_create(params, models.ToolsOzoneModerationGetRecord.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationDefs.RecordViewDetail)

    def get_records(
        self,
        params: t.Union[models.ToolsOzoneModerationGetRecords.Params, models.ToolsOzoneModerationGetRecords.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationGetRecords.Response':
        """Get details about some records.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationGetRecords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetRecords.Params',
            get_or_create(params, models.ToolsOzoneModerationGetRecords.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationGetRecords.Response)

    def get_repo(
        self,
        params: t.Union[models.ToolsOzoneModerationGetRepo.Params, models.ToolsOzoneModerationGetRepo.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationDefs.RepoViewDetail':
        """Get details about a repository.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationDefs.RepoViewDetail`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetRepo.Params',
            get_or_create(params, models.ToolsOzoneModerationGetRepo.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getRepo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationDefs.RepoViewDetail)

    def get_reporter_stats(
        self,
        params: t.Union[
            models.ToolsOzoneModerationGetReporterStats.Params, models.ToolsOzoneModerationGetReporterStats.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationGetReporterStats.Response':
        """Get reporter stats for a list of users.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationGetReporterStats.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetReporterStats.Params',
            get_or_create(params, models.ToolsOzoneModerationGetReporterStats.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getReporterStats', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationGetReporterStats.Response)

    def get_repos(
        self,
        params: t.Union[models.ToolsOzoneModerationGetRepos.Params, models.ToolsOzoneModerationGetRepos.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationGetRepos.Response':
        """Get details about some repositories.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationGetRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationGetRepos.Params',
            get_or_create(params, models.ToolsOzoneModerationGetRepos.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.getRepos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationGetRepos.Response)

    def query_events(
        self,
        params: t.Optional[
            t.Union[models.ToolsOzoneModerationQueryEvents.Params, models.ToolsOzoneModerationQueryEvents.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationQueryEvents.Response':
        """List moderation events related to a subject.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationQueryEvents.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationQueryEvents.Params',
            get_or_create(params, models.ToolsOzoneModerationQueryEvents.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.queryEvents', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationQueryEvents.Response)

    def query_statuses(
        self,
        params: t.Optional[
            t.Union[
                models.ToolsOzoneModerationQueryStatuses.Params, models.ToolsOzoneModerationQueryStatuses.ParamsDict
            ]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationQueryStatuses.Response':
        """View moderation statuses of subjects (record or repo).

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationQueryStatuses.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationQueryStatuses.Params',
            get_or_create(params, models.ToolsOzoneModerationQueryStatuses.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.queryStatuses', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationQueryStatuses.Response)

    def search_repos(
        self,
        params: t.Optional[
            t.Union[models.ToolsOzoneModerationSearchRepos.Params, models.ToolsOzoneModerationSearchRepos.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneModerationSearchRepos.Response':
        """Find repositories based on a search term.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneModerationSearchRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneModerationSearchRepos.Params',
            get_or_create(params, models.ToolsOzoneModerationSearchRepos.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.moderation.searchRepos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneModerationSearchRepos.Response)


class ToolsOzoneServerNamespace(NamespaceBase):
    def get_config(self, **kwargs: t.Any) -> 'models.ToolsOzoneServerGetConfig.Response':
        """Get details about ozone's server configuration.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneServerGetConfig.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        response = self._client.invoke_query(
            'tools.ozone.server.getConfig', output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneServerGetConfig.Response)


class ToolsOzoneSetNamespace(NamespaceBase):
    def add_values(
        self, data: t.Union[models.ToolsOzoneSetAddValues.Data, models.ToolsOzoneSetAddValues.DataDict], **kwargs: t.Any
    ) -> bool:
        """Add values to a specific set. Attempting to add values to a set that does not exist will result in an error.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneSetAddValues.Data', get_or_create(data, models.ToolsOzoneSetAddValues.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.set.addValues', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def delete_set(
        self, data: t.Union[models.ToolsOzoneSetDeleteSet.Data, models.ToolsOzoneSetDeleteSet.DataDict], **kwargs: t.Any
    ) -> 'models.ToolsOzoneSetDeleteSet.Response':
        """Delete an entire set. Attempting to delete a set that does not exist will result in an error.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSetDeleteSet.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneSetDeleteSet.Data', get_or_create(data, models.ToolsOzoneSetDeleteSet.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.set.deleteSet',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneSetDeleteSet.Response)

    def delete_values(
        self,
        data: t.Union[models.ToolsOzoneSetDeleteValues.Data, models.ToolsOzoneSetDeleteValues.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Delete values from a specific set. Attempting to delete values that are not in the set will not result in an error.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneSetDeleteValues.Data', get_or_create(data, models.ToolsOzoneSetDeleteValues.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.set.deleteValues', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def get_values(
        self,
        params: t.Union[models.ToolsOzoneSetGetValues.Params, models.ToolsOzoneSetGetValues.ParamsDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSetGetValues.Response':
        """Get a specific set and its values.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSetGetValues.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSetGetValues.Params', get_or_create(params, models.ToolsOzoneSetGetValues.Params)
        )
        response = self._client.invoke_query(
            'tools.ozone.set.getValues', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneSetGetValues.Response)

    def query_sets(
        self,
        params: t.Optional[
            t.Union[models.ToolsOzoneSetQuerySets.Params, models.ToolsOzoneSetQuerySets.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSetQuerySets.Response':
        """Query available sets.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSetQuerySets.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSetQuerySets.Params', get_or_create(params, models.ToolsOzoneSetQuerySets.Params)
        )
        response = self._client.invoke_query(
            'tools.ozone.set.querySets', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneSetQuerySets.Response)

    def upsert_set(self, data: models.ToolsOzoneSetDefs.Set, **kwargs: t.Any) -> 'models.ToolsOzoneSetDefs.SetView':
        """Create or update set metadata.

        Args:
            data: Input data (reference).
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSetDefs.SetView`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast('models.ToolsOzoneSetDefs.Set', get_or_create(data, models.ToolsOzoneSetDefs.Set))
        response = self._client.invoke_procedure(
            'tools.ozone.set.upsertSet',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneSetDefs.SetView)


class ToolsOzoneSettingNamespace(NamespaceBase):
    def list_options(
        self,
        params: t.Optional[
            t.Union[models.ToolsOzoneSettingListOptions.Params, models.ToolsOzoneSettingListOptions.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSettingListOptions.Response':
        """List settings with optional filtering.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSettingListOptions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSettingListOptions.Params',
            get_or_create(params, models.ToolsOzoneSettingListOptions.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.setting.listOptions', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneSettingListOptions.Response)

    def remove_options(
        self,
        data: t.Union[models.ToolsOzoneSettingRemoveOptions.Data, models.ToolsOzoneSettingRemoveOptions.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSettingRemoveOptions.Response':
        """Delete settings by key.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSettingRemoveOptions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneSettingRemoveOptions.Data',
            get_or_create(data, models.ToolsOzoneSettingRemoveOptions.Data),
        )
        response = self._client.invoke_procedure(
            'tools.ozone.setting.removeOptions',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneSettingRemoveOptions.Response)

    def upsert_option(
        self,
        data: t.Union[models.ToolsOzoneSettingUpsertOption.Data, models.ToolsOzoneSettingUpsertOption.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSettingUpsertOption.Response':
        """Create or update setting option.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSettingUpsertOption.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneSettingUpsertOption.Data', get_or_create(data, models.ToolsOzoneSettingUpsertOption.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.setting.upsertOption',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneSettingUpsertOption.Response)


class ToolsOzoneSignatureNamespace(NamespaceBase):
    def find_correlation(
        self,
        params: t.Union[
            models.ToolsOzoneSignatureFindCorrelation.Params, models.ToolsOzoneSignatureFindCorrelation.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSignatureFindCorrelation.Response':
        """Find all correlated threat signatures between 2 or more accounts.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSignatureFindCorrelation.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSignatureFindCorrelation.Params',
            get_or_create(params, models.ToolsOzoneSignatureFindCorrelation.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.signature.findCorrelation', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneSignatureFindCorrelation.Response)

    def find_related_accounts(
        self,
        params: t.Union[
            models.ToolsOzoneSignatureFindRelatedAccounts.Params,
            models.ToolsOzoneSignatureFindRelatedAccounts.ParamsDict,
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSignatureFindRelatedAccounts.Response':
        """Get accounts that share some matching threat signatures with the root account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSignatureFindRelatedAccounts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSignatureFindRelatedAccounts.Params',
            get_or_create(params, models.ToolsOzoneSignatureFindRelatedAccounts.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.signature.findRelatedAccounts',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneSignatureFindRelatedAccounts.Response)

    def search_accounts(
        self,
        params: t.Union[
            models.ToolsOzoneSignatureSearchAccounts.Params, models.ToolsOzoneSignatureSearchAccounts.ParamsDict
        ],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneSignatureSearchAccounts.Response':
        """Search for accounts that match one or more threat signature values.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneSignatureSearchAccounts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneSignatureSearchAccounts.Params',
            get_or_create(params, models.ToolsOzoneSignatureSearchAccounts.Params),
        )
        response = self._client.invoke_query(
            'tools.ozone.signature.searchAccounts', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneSignatureSearchAccounts.Response)


class ToolsOzoneTeamNamespace(NamespaceBase):
    def add_member(
        self,
        data: t.Union[models.ToolsOzoneTeamAddMember.Data, models.ToolsOzoneTeamAddMember.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneTeamDefs.Member':
        """Add a member to the ozone team. Requires admin role.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneTeamDefs.Member`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneTeamAddMember.Data', get_or_create(data, models.ToolsOzoneTeamAddMember.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.team.addMember',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneTeamDefs.Member)

    def delete_member(
        self,
        data: t.Union[models.ToolsOzoneTeamDeleteMember.Data, models.ToolsOzoneTeamDeleteMember.DataDict],
        **kwargs: t.Any,
    ) -> bool:
        """Delete a member from ozone team. Requires admin role.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneTeamDeleteMember.Data', get_or_create(data, models.ToolsOzoneTeamDeleteMember.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.team.deleteMember', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def list_members(
        self,
        params: t.Optional[
            t.Union[models.ToolsOzoneTeamListMembers.Params, models.ToolsOzoneTeamListMembers.ParamsDict]
        ] = None,
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneTeamListMembers.Response':
        """List all members with access to the ozone service.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneTeamListMembers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        params_model = t.cast(
            'models.ToolsOzoneTeamListMembers.Params', get_or_create(params, models.ToolsOzoneTeamListMembers.Params)
        )
        response = self._client.invoke_query(
            'tools.ozone.team.listMembers', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ToolsOzoneTeamListMembers.Response)

    def update_member(
        self,
        data: t.Union[models.ToolsOzoneTeamUpdateMember.Data, models.ToolsOzoneTeamUpdateMember.DataDict],
        **kwargs: t.Any,
    ) -> 'models.ToolsOzoneTeamDefs.Member':
        """Update a member in the ozone service. Requires admin role.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ToolsOzoneTeamDefs.Member`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """
        data_model = t.cast(
            'models.ToolsOzoneTeamUpdateMember.Data', get_or_create(data, models.ToolsOzoneTeamUpdateMember.Data)
        )
        response = self._client.invoke_procedure(
            'tools.ozone.team.updateMember',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ToolsOzoneTeamDefs.Member)
