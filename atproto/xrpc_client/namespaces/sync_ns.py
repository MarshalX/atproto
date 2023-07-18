##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from atproto.xrpc_client import models
from atproto.xrpc_client.models.utils import get_or_create_model, get_response_model
from atproto.xrpc_client.namespaces.base import NamespaceBase

if t.TYPE_CHECKING:
    from atproto.xrpc_client.client.raw import ClientRaw


class AppNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.bsky = BskyNamespace(self._client)


class BskyNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.actor = ActorNamespace(self._client)
        self.feed = FeedNamespace(self._client)
        self.graph = GraphNamespace(self._client)
        self.notification = NotificationNamespace(self._client)
        self.unspecced = UnspeccedNamespace(self._client)


class ActorNamespace(NamespaceBase):
    def get_preferences(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyActorGetPreferences.Params']] = None, **kwargs
    ) -> 'models.AppBskyActorGetPreferences.Response':
        """Get private preferences attached to the account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetPreferences.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorGetPreferences.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.getPreferences', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetPreferences.Response)

    def get_profile(
        self, params: t.Union[dict, 'models.AppBskyActorGetProfile.Params'], **kwargs
    ) -> 'models.AppBskyActorGetProfile.ResponseRef':
        """Get profile.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetProfile.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorGetProfile.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.getProfile', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetProfile.ResponseRef)

    def get_profiles(
        self, params: t.Union[dict, 'models.AppBskyActorGetProfiles.Params'], **kwargs
    ) -> 'models.AppBskyActorGetProfiles.Response':
        """Get profiles.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetProfiles.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorGetProfiles.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.getProfiles', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetProfiles.Response)

    def get_suggestions(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyActorGetSuggestions.Params']] = None, **kwargs
    ) -> 'models.AppBskyActorGetSuggestions.Response':
        """Get a list of actors suggested for following. Used in discovery UIs.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorGetSuggestions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorGetSuggestions.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.getSuggestions', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorGetSuggestions.Response)

    def put_preferences(self, data: t.Union[dict, 'models.AppBskyActorPutPreferences.Data'], **kwargs) -> bool:
        """Sets the private preferences attached to the account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyActorPutPreferences.Data)
        response = self._client.invoke_procedure(
            'app.bsky.actor.putPreferences', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def search_actors(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyActorSearchActors.Params']] = None, **kwargs
    ) -> 'models.AppBskyActorSearchActors.Response':
        """Find actors matching search criteria.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActors.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorSearchActors.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.searchActors', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActors.Response)

    def search_actors_typeahead(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyActorSearchActorsTypeahead.Params']] = None, **kwargs
    ) -> 'models.AppBskyActorSearchActorsTypeahead.Response':
        """Find actor suggestions for a search term.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyActorSearchActorsTypeahead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyActorSearchActorsTypeahead.Params)
        response = self._client.invoke_query(
            'app.bsky.actor.searchActorsTypeahead', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyActorSearchActorsTypeahead.Response)


class FeedNamespace(NamespaceBase):
    def describe_feed_generator(self, **kwargs) -> 'models.AppBskyFeedDescribeFeedGenerator.Response':
        """Returns information about a given feed generator including TOS & offered feed URIs.

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
        self, params: t.Union[dict, 'models.AppBskyFeedGetActorFeeds.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetActorFeeds.Response':
        """Retrieve a list of feeds created by a given actor.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetActorFeeds.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetActorFeeds.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getActorFeeds', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetActorFeeds.Response)

    def get_author_feed(
        self, params: t.Union[dict, 'models.AppBskyFeedGetAuthorFeed.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetAuthorFeed.Response':
        """A view of an actor's feed.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetAuthorFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetAuthorFeed.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getAuthorFeed', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetAuthorFeed.Response)

    def get_feed(
        self, params: t.Union[dict, 'models.AppBskyFeedGetFeed.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetFeed.Response':
        """Compose and hydrate a feed from a user's selected feed generator.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeed.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetFeed.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getFeed', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeed.Response)

    def get_feed_generator(
        self, params: t.Union[dict, 'models.AppBskyFeedGetFeedGenerator.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetFeedGenerator.Response':
        """Get information about a specific feed offered by a feed generator, such as its online status.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeedGenerator.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetFeedGenerator.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedGenerator', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedGenerator.Response)

    def get_feed_generators(
        self, params: t.Union[dict, 'models.AppBskyFeedGetFeedGenerators.Params'], **kwargs
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

        params_model = get_or_create_model(params, models.AppBskyFeedGetFeedGenerators.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedGenerators', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedGenerators.Response)

    def get_feed_skeleton(
        self, params: t.Union[dict, 'models.AppBskyFeedGetFeedSkeleton.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetFeedSkeleton.Response':
        """A skeleton of a feed provided by a feed generator.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetFeedSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetFeedSkeleton.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getFeedSkeleton', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetFeedSkeleton.Response)

    def get_likes(
        self, params: t.Union[dict, 'models.AppBskyFeedGetLikes.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetLikes.Response':
        """Get likes.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetLikes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetLikes.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getLikes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetLikes.Response)

    def get_post_thread(
        self, params: t.Union[dict, 'models.AppBskyFeedGetPostThread.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetPostThread.Response':
        """Get post thread.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPostThread.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetPostThread.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getPostThread', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPostThread.Response)

    def get_posts(
        self, params: t.Union[dict, 'models.AppBskyFeedGetPosts.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetPosts.Response':
        """A view of an actor's feed.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetPosts.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetPosts.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getPosts', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetPosts.Response)

    def get_reposted_by(
        self, params: t.Union[dict, 'models.AppBskyFeedGetRepostedBy.Params'], **kwargs
    ) -> 'models.AppBskyFeedGetRepostedBy.Response':
        """Get reposted by.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetRepostedBy.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetRepostedBy.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getRepostedBy', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetRepostedBy.Response)

    def get_timeline(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyFeedGetTimeline.Params']] = None, **kwargs
    ) -> 'models.AppBskyFeedGetTimeline.Response':
        """A view of the user's home timeline.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyFeedGetTimeline.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyFeedGetTimeline.Params)
        response = self._client.invoke_query(
            'app.bsky.feed.getTimeline', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyFeedGetTimeline.Response)


class GraphNamespace(NamespaceBase):
    def get_blocks(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyGraphGetBlocks.Params']] = None, **kwargs
    ) -> 'models.AppBskyGraphGetBlocks.Response':
        """Who is the requester's account blocking?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetBlocks.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getBlocks', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetBlocks.Response)

    def get_followers(
        self, params: t.Union[dict, 'models.AppBskyGraphGetFollowers.Params'], **kwargs
    ) -> 'models.AppBskyGraphGetFollowers.Response':
        """Who is following an actor?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollowers.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetFollowers.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getFollowers', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollowers.Response)

    def get_follows(
        self, params: t.Union[dict, 'models.AppBskyGraphGetFollows.Params'], **kwargs
    ) -> 'models.AppBskyGraphGetFollows.Response':
        """Who is an actor following?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetFollows.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetFollows.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getFollows', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetFollows.Response)

    def get_list(
        self, params: t.Union[dict, 'models.AppBskyGraphGetList.Params'], **kwargs
    ) -> 'models.AppBskyGraphGetList.Response':
        """Fetch a list of actors.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetList.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetList.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getList', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetList.Response)

    def get_list_mutes(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyGraphGetListMutes.Params']] = None, **kwargs
    ) -> 'models.AppBskyGraphGetListMutes.Response':
        """Which lists is the requester's account muting?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetListMutes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetListMutes.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getListMutes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetListMutes.Response)

    def get_lists(
        self, params: t.Union[dict, 'models.AppBskyGraphGetLists.Params'], **kwargs
    ) -> 'models.AppBskyGraphGetLists.Response':
        """Fetch a list of lists that belong to an actor.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetLists.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetLists.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getLists', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetLists.Response)

    def get_mutes(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyGraphGetMutes.Params']] = None, **kwargs
    ) -> 'models.AppBskyGraphGetMutes.Response':
        """Who does the viewer mute?

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyGraphGetMutes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyGraphGetMutes.Params)
        response = self._client.invoke_query(
            'app.bsky.graph.getMutes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyGraphGetMutes.Response)

    def mute_actor(self, data: t.Union[dict, 'models.AppBskyGraphMuteActor.Data'], **kwargs) -> bool:
        """Mute an actor by did or handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyGraphMuteActor.Data)
        response = self._client.invoke_procedure(
            'app.bsky.graph.muteActor', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def mute_actor_list(self, data: t.Union[dict, 'models.AppBskyGraphMuteActorList.Data'], **kwargs) -> bool:
        """Mute a list of actors.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyGraphMuteActorList.Data)
        response = self._client.invoke_procedure(
            'app.bsky.graph.muteActorList', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def unmute_actor(self, data: t.Union[dict, 'models.AppBskyGraphUnmuteActor.Data'], **kwargs) -> bool:
        """Unmute an actor by did or handle.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyGraphUnmuteActor.Data)
        response = self._client.invoke_procedure(
            'app.bsky.graph.unmuteActor', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def unmute_actor_list(self, data: t.Union[dict, 'models.AppBskyGraphUnmuteActorList.Data'], **kwargs) -> bool:
        """Unmute a list of actors.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyGraphUnmuteActorList.Data)
        response = self._client.invoke_procedure(
            'app.bsky.graph.unmuteActorList', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class UnspeccedNamespace(NamespaceBase):
    def get_popular(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyUnspeccedGetPopular.Params']] = None, **kwargs
    ) -> 'models.AppBskyUnspeccedGetPopular.Response':
        """An unspecced view of globally popular items.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetPopular.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyUnspeccedGetPopular.Params)
        response = self._client.invoke_query(
            'app.bsky.unspecced.getPopular', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetPopular.Response)

    def get_popular_feed_generators(
        self,
        params: t.Optional[t.Union[dict, 'models.AppBskyUnspeccedGetPopularFeedGenerators.Params']] = None,
        **kwargs,
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

        params_model = get_or_create_model(params, models.AppBskyUnspeccedGetPopularFeedGenerators.Params)
        response = self._client.invoke_query(
            'app.bsky.unspecced.getPopularFeedGenerators',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.AppBskyUnspeccedGetPopularFeedGenerators.Response)

    def get_timeline_skeleton(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyUnspeccedGetTimelineSkeleton.Params']] = None, **kwargs
    ) -> 'models.AppBskyUnspeccedGetTimelineSkeleton.Response':
        """A skeleton of a timeline - UNSPECCED & WILL GO AWAY SOON.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyUnspeccedGetTimelineSkeleton.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyUnspeccedGetTimelineSkeleton.Params)
        response = self._client.invoke_query(
            'app.bsky.unspecced.getTimelineSkeleton', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyUnspeccedGetTimelineSkeleton.Response)


class NotificationNamespace(NamespaceBase):
    def get_unread_count(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyNotificationGetUnreadCount.Params']] = None, **kwargs
    ) -> 'models.AppBskyNotificationGetUnreadCount.Response':
        """Get unread count.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationGetUnreadCount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyNotificationGetUnreadCount.Params)
        response = self._client.invoke_query(
            'app.bsky.notification.getUnreadCount', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationGetUnreadCount.Response)

    def list_notifications(
        self, params: t.Optional[t.Union[dict, 'models.AppBskyNotificationListNotifications.Params']] = None, **kwargs
    ) -> 'models.AppBskyNotificationListNotifications.Response':
        """List notifications.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.AppBskyNotificationListNotifications.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.AppBskyNotificationListNotifications.Params)
        response = self._client.invoke_query(
            'app.bsky.notification.listNotifications', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.AppBskyNotificationListNotifications.Response)

    def update_seen(self, data: t.Union[dict, 'models.AppBskyNotificationUpdateSeen.Data'], **kwargs) -> bool:
        """Notify server that the user has seen notifications.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.AppBskyNotificationUpdateSeen.Data)
        response = self._client.invoke_procedure(
            'app.bsky.notification.updateSeen', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ComNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.atproto = AtprotoNamespace(self._client)


class AtprotoNamespace(NamespaceBase):
    def __init__(self, client: 'ClientRaw') -> None:
        super().__init__(client)
        self.admin = AdminNamespace(self._client)
        self.identity = IdentityNamespace(self._client)
        self.label = LabelNamespace(self._client)
        self.moderation = ModerationNamespace(self._client)
        self.repo = RepoNamespace(self._client)
        self.server = ServerNamespace(self._client)
        self.sync = SyncNamespace(self._client)


class SyncNamespace(NamespaceBase):
    def get_blob(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetBlob.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetBlob.Response':
        """Get a blob associated with a given repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlob.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetBlob.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getBlob', params=params_model, output_encoding='*/*', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlob.Response)

    def get_blocks(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetBlocks.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetBlocks.Response':
        """Gets blocks from a given repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetBlocks.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetBlocks.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getBlocks', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetBlocks.Response)

    def get_checkout(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetCheckout.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetCheckout.Response':
        """Gets the repo state.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetCheckout.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetCheckout.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getCheckout', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetCheckout.Response)

    def get_commit_path(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetCommitPath.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetCommitPath.Response':
        """Gets the path of repo commits.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetCommitPath.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetCommitPath.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getCommitPath', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetCommitPath.Response)

    def get_head(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetHead.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetHead.Response':
        """Gets the current HEAD CID of a repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetHead.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetHead.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getHead', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetHead.Response)

    def get_record(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetRecord.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetRecord.Response':
        """Gets blocks needed for existence or non-existence of record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetRecord.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getRecord', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRecord.Response)

    def get_repo(
        self, params: t.Union[dict, 'models.ComAtprotoSyncGetRepo.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncGetRepo.Response':
        """Gets the repo state.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncGetRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncGetRepo.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.getRepo', params=params_model, output_encoding='application/vnd.ipld.car', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncGetRepo.Response)

    def list_blobs(
        self, params: t.Union[dict, 'models.ComAtprotoSyncListBlobs.Params'], **kwargs
    ) -> 'models.ComAtprotoSyncListBlobs.Response':
        """List blob cids for some range of commits.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListBlobs.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncListBlobs.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.listBlobs', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListBlobs.Response)

    def list_repos(
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncListRepos.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoSyncListRepos.Response':
        """List dids and root cids of hosted repos.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoSyncListRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoSyncListRepos.Params)
        response = self._client.invoke_query(
            'com.atproto.sync.listRepos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoSyncListRepos.Response)

    def notify_of_update(self, data: t.Union[dict, 'models.ComAtprotoSyncNotifyOfUpdate.Data'], **kwargs) -> bool:
        """Notify a crawling service of a recent update. Often when a long break between updates causes the connection with the crawling service to break.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoSyncNotifyOfUpdate.Data)
        response = self._client.invoke_procedure(
            'com.atproto.sync.notifyOfUpdate', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def request_crawl(self, data: t.Union[dict, 'models.ComAtprotoSyncRequestCrawl.Data'], **kwargs) -> bool:
        """Request a service to persistently crawl hosted repos.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoSyncRequestCrawl.Data)
        response = self._client.invoke_procedure(
            'com.atproto.sync.requestCrawl', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class AdminNamespace(NamespaceBase):
    def disable_account_invites(
        self, data: t.Union[dict, 'models.ComAtprotoAdminDisableAccountInvites.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoAdminDisableAccountInvites.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.disableAccountInvites', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def disable_invite_codes(
        self, data: t.Optional[t.Union[dict, 'models.ComAtprotoAdminDisableInviteCodes.Data']] = None, **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoAdminDisableInviteCodes.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.disableInviteCodes', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def enable_account_invites(
        self, data: t.Union[dict, 'models.ComAtprotoAdminEnableAccountInvites.Data'], **kwargs
    ) -> bool:
        """Re-enable an accounts ability to receive invite codes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminEnableAccountInvites.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.enableAccountInvites', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def get_invite_codes(
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoAdminGetInviteCodes.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoAdminGetInviteCodes.Response':
        """Admin view of invite codes.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetInviteCodes.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getInviteCodes', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetInviteCodes.Response)

    def get_moderation_action(
        self, params: t.Union[dict, 'models.ComAtprotoAdminGetModerationAction.Params'], **kwargs
    ) -> 'models.ComAtprotoAdminGetModerationAction.ResponseRef':
        """View details about a moderation action.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetModerationAction.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getModerationAction', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationAction.ResponseRef)

    def get_moderation_actions(
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoAdminGetModerationActions.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoAdminGetModerationActions.Response':
        """List moderation actions related to a subject.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationActions.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetModerationActions.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getModerationActions', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationActions.Response)

    def get_moderation_report(
        self, params: t.Union[dict, 'models.ComAtprotoAdminGetModerationReport.Params'], **kwargs
    ) -> 'models.ComAtprotoAdminGetModerationReport.ResponseRef':
        """View details about a moderation report.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationReport.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetModerationReport.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getModerationReport', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationReport.ResponseRef)

    def get_moderation_reports(
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoAdminGetModerationReports.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoAdminGetModerationReports.Response':
        """List moderation reports related to a subject.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetModerationReports.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetModerationReports.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getModerationReports', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetModerationReports.Response)

    def get_record(
        self, params: t.Union[dict, 'models.ComAtprotoAdminGetRecord.Params'], **kwargs
    ) -> 'models.ComAtprotoAdminGetRecord.ResponseRef':
        """View details about a record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetRecord.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetRecord.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetRecord.ResponseRef)

    def get_repo(
        self, params: t.Union[dict, 'models.ComAtprotoAdminGetRepo.Params'], **kwargs
    ) -> 'models.ComAtprotoAdminGetRepo.ResponseRef':
        """View details about a repository.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminGetRepo.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminGetRepo.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.getRepo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminGetRepo.ResponseRef)

    def rebase_repo(self, data: t.Union[dict, 'models.ComAtprotoAdminRebaseRepo.Data'], **kwargs) -> bool:
        """Administrative action to rebase an account's repo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminRebaseRepo.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.rebaseRepo', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def resolve_moderation_reports(
        self, data: t.Union[dict, 'models.ComAtprotoAdminResolveModerationReports.Data'], **kwargs
    ) -> 'models.ComAtprotoAdminResolveModerationReports.ResponseRef':
        """Resolve moderation reports by an action.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminResolveModerationReports.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminResolveModerationReports.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.resolveModerationReports',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminResolveModerationReports.ResponseRef)

    def reverse_moderation_action(
        self, data: t.Union[dict, 'models.ComAtprotoAdminReverseModerationAction.Data'], **kwargs
    ) -> 'models.ComAtprotoAdminReverseModerationAction.ResponseRef':
        """Reverse a moderation action.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminReverseModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminReverseModerationAction.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.reverseModerationAction',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminReverseModerationAction.ResponseRef)

    def search_repos(
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoAdminSearchRepos.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoAdminSearchRepos.Response':
        """Find repositories based on a search term.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminSearchRepos.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoAdminSearchRepos.Params)
        response = self._client.invoke_query(
            'com.atproto.admin.searchRepos', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoAdminSearchRepos.Response)

    def send_email(
        self, data: t.Union[dict, 'models.ComAtprotoAdminSendEmail.Data'], **kwargs
    ) -> 'models.ComAtprotoAdminSendEmail.Response':
        """Send email to a user's primary email address.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminSendEmail.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminSendEmail.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.sendEmail',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminSendEmail.Response)

    def take_moderation_action(
        self, data: t.Union[dict, 'models.ComAtprotoAdminTakeModerationAction.Data'], **kwargs
    ) -> 'models.ComAtprotoAdminTakeModerationAction.ResponseRef':
        """Take a moderation action on a repo.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoAdminTakeModerationAction.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoAdminTakeModerationAction.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.takeModerationAction',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoAdminTakeModerationAction.ResponseRef)

    def update_account_email(
        self, data: t.Union[dict, 'models.ComAtprotoAdminUpdateAccountEmail.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoAdminUpdateAccountEmail.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateAccountEmail', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def update_account_handle(
        self, data: t.Union[dict, 'models.ComAtprotoAdminUpdateAccountHandle.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoAdminUpdateAccountHandle.Data)
        response = self._client.invoke_procedure(
            'com.atproto.admin.updateAccountHandle', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ServerNamespace(NamespaceBase):
    def create_account(
        self, data: t.Union[dict, 'models.ComAtprotoServerCreateAccount.Data'], **kwargs
    ) -> 'models.ComAtprotoServerCreateAccount.Response':
        """Create an account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAccount.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerCreateAccount.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.createAccount',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAccount.Response)

    def create_app_password(
        self, data: t.Union[dict, 'models.ComAtprotoServerCreateAppPassword.Data'], **kwargs
    ) -> 'models.ComAtprotoServerCreateAppPassword.ResponseRef':
        """Create an app-specific password.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateAppPassword.ResponseRef`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerCreateAppPassword.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.createAppPassword',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateAppPassword.ResponseRef)

    def create_invite_code(
        self, data: t.Union[dict, 'models.ComAtprotoServerCreateInviteCode.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoServerCreateInviteCode.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.createInviteCode',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCode.Response)

    def create_invite_codes(
        self, data: t.Union[dict, 'models.ComAtprotoServerCreateInviteCodes.Data'], **kwargs
    ) -> 'models.ComAtprotoServerCreateInviteCodes.Response':
        """Create an invite code.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerCreateInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerCreateInviteCodes.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.createInviteCodes',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateInviteCodes.Response)

    def create_session(
        self, data: t.Union[dict, 'models.ComAtprotoServerCreateSession.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoServerCreateSession.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.createSession',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerCreateSession.Response)

    def delete_account(self, data: t.Union[dict, 'models.ComAtprotoServerDeleteAccount.Data'], **kwargs) -> bool:
        """Delete a user account with a token and password.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerDeleteAccount.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.deleteAccount', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def delete_session(self, **kwargs) -> bool:
        """Delete the current session.

        Args:
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        response = self._client.invoke_procedure('com.atproto.server.deleteSession', **kwargs)
        return get_response_model(response, bool)

    def describe_server(self, **kwargs) -> 'models.ComAtprotoServerDescribeServer.Response':
        """Get a document describing the service's accounts configuration.

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
        self, params: t.Optional[t.Union[dict, 'models.ComAtprotoServerGetAccountInviteCodes.Params']] = None, **kwargs
    ) -> 'models.ComAtprotoServerGetAccountInviteCodes.Response':
        """Get all invite codes for a given account.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoServerGetAccountInviteCodes.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoServerGetAccountInviteCodes.Params)
        response = self._client.invoke_query(
            'com.atproto.server.getAccountInviteCodes',
            params=params_model,
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoServerGetAccountInviteCodes.Response)

    def get_session(self, **kwargs) -> 'models.ComAtprotoServerGetSession.Response':
        """Get information about the current session.

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

    def list_app_passwords(self, **kwargs) -> 'models.ComAtprotoServerListAppPasswords.Response':
        """List all app-specific passwords.

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

    def refresh_session(self, **kwargs) -> 'models.ComAtprotoServerRefreshSession.Response':
        """Refresh an authentication session.

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

    def request_account_delete(self, **kwargs) -> bool:
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

    def request_password_reset(
        self, data: t.Union[dict, 'models.ComAtprotoServerRequestPasswordReset.Data'], **kwargs
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

        data_model = get_or_create_model(data, models.ComAtprotoServerRequestPasswordReset.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.requestPasswordReset', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def reset_password(self, data: t.Union[dict, 'models.ComAtprotoServerResetPassword.Data'], **kwargs) -> bool:
        """Reset a user account password using a token.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerResetPassword.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.resetPassword', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def revoke_app_password(
        self, data: t.Union[dict, 'models.ComAtprotoServerRevokeAppPassword.Data'], **kwargs
    ) -> bool:
        """Revoke an app-specific password by name.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoServerRevokeAppPassword.Data)
        response = self._client.invoke_procedure(
            'com.atproto.server.revokeAppPassword', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class RepoNamespace(NamespaceBase):
    def apply_writes(self, data: t.Union[dict, 'models.ComAtprotoRepoApplyWrites.Data'], **kwargs) -> bool:
        """Apply a batch transaction of creates, updates, and deletes.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoRepoApplyWrites.Data)
        response = self._client.invoke_procedure(
            'com.atproto.repo.applyWrites', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def create_record(
        self, data: t.Union[dict, 'models.ComAtprotoRepoCreateRecord.Data'], **kwargs
    ) -> 'models.ComAtprotoRepoCreateRecord.Response':
        """Create a new record.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoCreateRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoRepoCreateRecord.Data)
        response = self._client.invoke_procedure(
            'com.atproto.repo.createRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoCreateRecord.Response)

    def delete_record(self, data: t.Union[dict, 'models.ComAtprotoRepoDeleteRecord.Data'], **kwargs) -> bool:
        """Delete a record, or ensure it doesn't exist.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoRepoDeleteRecord.Data)
        response = self._client.invoke_procedure(
            'com.atproto.repo.deleteRecord', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def describe_repo(
        self, params: t.Union[dict, 'models.ComAtprotoRepoDescribeRepo.Params'], **kwargs
    ) -> 'models.ComAtprotoRepoDescribeRepo.Response':
        """Get information about the repo, including the list of collections.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoDescribeRepo.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoRepoDescribeRepo.Params)
        response = self._client.invoke_query(
            'com.atproto.repo.describeRepo', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoDescribeRepo.Response)

    def get_record(
        self, params: t.Union[dict, 'models.ComAtprotoRepoGetRecord.Params'], **kwargs
    ) -> 'models.ComAtprotoRepoGetRecord.Response':
        """Get a record.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoGetRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoRepoGetRecord.Params)
        response = self._client.invoke_query(
            'com.atproto.repo.getRecord', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoGetRecord.Response)

    def list_records(
        self, params: t.Union[dict, 'models.ComAtprotoRepoListRecords.Params'], **kwargs
    ) -> 'models.ComAtprotoRepoListRecords.Response':
        """List a range of records in a collection.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoListRecords.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoRepoListRecords.Params)
        response = self._client.invoke_query(
            'com.atproto.repo.listRecords', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoRepoListRecords.Response)

    def put_record(
        self, data: t.Union[dict, 'models.ComAtprotoRepoPutRecord.Data'], **kwargs
    ) -> 'models.ComAtprotoRepoPutRecord.Response':
        """Write a record, creating or updating it as needed.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoRepoPutRecord.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoRepoPutRecord.Data)
        response = self._client.invoke_procedure(
            'com.atproto.repo.putRecord',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoRepoPutRecord.Response)

    def rebase_repo(self, data: t.Union[dict, 'models.ComAtprotoRepoRebaseRepo.Data'], **kwargs) -> bool:
        """Simple rebase of repo that deletes history.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoRepoRebaseRepo.Data)
        response = self._client.invoke_procedure(
            'com.atproto.repo.rebaseRepo', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)

    def upload_blob(
        self, data: 'models.ComAtprotoRepoUploadBlob.Data', **kwargs
    ) -> 'models.ComAtprotoRepoUploadBlob.Response':
        """Upload a new blob to be added to repo in a later request.

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


class IdentityNamespace(NamespaceBase):
    def resolve_handle(
        self, params: t.Union[dict, 'models.ComAtprotoIdentityResolveHandle.Params'], **kwargs
    ) -> 'models.ComAtprotoIdentityResolveHandle.Response':
        """Provides the DID of a repo.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoIdentityResolveHandle.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoIdentityResolveHandle.Params)
        response = self._client.invoke_query(
            'com.atproto.identity.resolveHandle', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoIdentityResolveHandle.Response)

    def update_handle(self, data: t.Union[dict, 'models.ComAtprotoIdentityUpdateHandle.Data'], **kwargs) -> bool:
        """Updates the handle of the account.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`bool`: Success status.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoIdentityUpdateHandle.Data)
        response = self._client.invoke_procedure(
            'com.atproto.identity.updateHandle', data=data_model, input_encoding='application/json', **kwargs
        )
        return get_response_model(response, bool)


class ModerationNamespace(NamespaceBase):
    def create_report(
        self, data: t.Union[dict, 'models.ComAtprotoModerationCreateReport.Data'], **kwargs
    ) -> 'models.ComAtprotoModerationCreateReport.Response':
        """Report a repo or a record.

        Args:
            data: Input data.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoModerationCreateReport.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        data_model = get_or_create_model(data, models.ComAtprotoModerationCreateReport.Data)
        response = self._client.invoke_procedure(
            'com.atproto.moderation.createReport',
            data=data_model,
            input_encoding='application/json',
            output_encoding='application/json',
            **kwargs,
        )
        return get_response_model(response, models.ComAtprotoModerationCreateReport.Response)


class LabelNamespace(NamespaceBase):
    def query_labels(
        self, params: t.Union[dict, 'models.ComAtprotoLabelQueryLabels.Params'], **kwargs
    ) -> 'models.ComAtprotoLabelQueryLabels.Response':
        """Find labels relevant to the provided URI patterns.

        Args:
            params: Parameters.
            **kwargs: Arbitrary arguments to HTTP request.

        Returns:
            :obj:`models.ComAtprotoLabelQueryLabels.Response`: Output model.

        Raises:
            :class:`atproto.exceptions.AtProtocolError`: Base exception.
        """

        params_model = get_or_create_model(params, models.ComAtprotoLabelQueryLabels.Params)
        response = self._client.invoke_query(
            'com.atproto.label.queryLabels', params=params_model, output_encoding='application/json', **kwargs
        )
        return get_response_model(response, models.ComAtprotoLabelQueryLabels.Response)
