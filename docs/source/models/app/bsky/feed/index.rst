app.bsky.feed
=============

Posts, likes, reposts, threads, and feed generators.

.. automodule:: atproto_client.models.app.bsky.feed
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/app/bsky/feed/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` describeFeedGenerator
      :link: /models/app/bsky/feed/describeFeedGenerator
      :link-type: doc

      Get information about a feed generator, including policies and offered feed URIs.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` generator
      :link: /models/app/bsky/feed/generator
      :link-type: doc

      Record declaring of the existence of a feed generator, and containing metadata about it.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getActorFeeds
      :link: /models/app/bsky/feed/getActorFeeds
      :link-type: doc

      Get a list of feeds (feed generator records) created by the actor (in the actor's repo).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getActorLikes
      :link: /models/app/bsky/feed/getActorLikes
      :link-type: doc

      Get a list of posts liked by an actor.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getAuthorFeed
      :link: /models/app/bsky/feed/getAuthorFeed
      :link-type: doc

      Get a view of an actor's 'author feed' (post and reposts by the author).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFeed
      :link: /models/app/bsky/feed/getFeed
      :link-type: doc

      Get a hydrated feed from an actor's selected feed generator.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFeedGenerator
      :link: /models/app/bsky/feed/getFeedGenerator
      :link-type: doc

      Get information about a feed generator.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFeedGenerators
      :link: /models/app/bsky/feed/getFeedGenerators
      :link-type: doc

      Get information about a list of feed generators.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFeedSkeleton
      :link: /models/app/bsky/feed/getFeedSkeleton
      :link-type: doc

      Get a skeleton of a feed provided by a feed generator.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getLikes
      :link: /models/app/bsky/feed/getLikes
      :link-type: doc

      Get like records which reference a subject (by AT-URI and CID).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getListFeed
      :link: /models/app/bsky/feed/getListFeed
      :link-type: doc

      Get a feed of recent posts from a list (posts and reposts from any actors on the list).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getPostThread
      :link: /models/app/bsky/feed/getPostThread
      :link-type: doc

      Get posts in a thread.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getPosts
      :link: /models/app/bsky/feed/getPosts
      :link-type: doc

      Gets post views for a specified list of posts (by AT-URI).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getQuotes
      :link: /models/app/bsky/feed/getQuotes
      :link-type: doc

      Get a list of quotes for a given post.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRepostedBy
      :link: /models/app/bsky/feed/getRepostedBy
      :link-type: doc

      Get a list of reposts for a given post.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSuggestedFeeds
      :link: /models/app/bsky/feed/getSuggestedFeeds
      :link-type: doc

      Get a list of suggested feeds (feed generators) for the requesting account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getTimeline
      :link: /models/app/bsky/feed/getTimeline
      :link-type: doc

      Get a view of the requesting account's home timeline.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` like
      :link: /models/app/bsky/feed/like
      :link-type: doc

      Record declaring a 'like' of a piece of subject content.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` post
      :link: /models/app/bsky/feed/post
      :link-type: doc

      Record containing a Bluesky post.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` postgate
      :link: /models/app/bsky/feed/postgate
      :link-type: doc

      Record defining interaction rules for a post.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` repost
      :link: /models/app/bsky/feed/repost
      :link-type: doc

      Record representing a 'repost' of an existing Bluesky post.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` searchPosts
      :link: /models/app/bsky/feed/searchPosts
      :link-type: doc

      Find posts matching search criteria, returning views of those posts.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` searchPostsV2
      :link: /models/app/bsky/feed/searchPostsV2
      :link-type: doc

      Find posts matching a search query or filters, returning search hits for matching post records.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` sendInteractions
      :link: /models/app/bsky/feed/sendInteractions
      :link-type: doc

      Send information about interactions with feed items back to the feed generator that served them.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` threadgate
      :link: /models/app/bsky/feed/threadgate
      :link-type: doc

      Record defining interaction gating rules for a thread (aka, reply controls).

.. toctree::
   :hidden:
   :maxdepth: 1

   /models/app/bsky/feed/defs
   /models/app/bsky/feed/describeFeedGenerator
   /models/app/bsky/feed/generator
   /models/app/bsky/feed/getActorFeeds
   /models/app/bsky/feed/getActorLikes
   /models/app/bsky/feed/getAuthorFeed
   /models/app/bsky/feed/getFeed
   /models/app/bsky/feed/getFeedGenerator
   /models/app/bsky/feed/getFeedGenerators
   /models/app/bsky/feed/getFeedSkeleton
   /models/app/bsky/feed/getLikes
   /models/app/bsky/feed/getListFeed
   /models/app/bsky/feed/getPostThread
   /models/app/bsky/feed/getPosts
   /models/app/bsky/feed/getQuotes
   /models/app/bsky/feed/getRepostedBy
   /models/app/bsky/feed/getSuggestedFeeds
   /models/app/bsky/feed/getTimeline
   /models/app/bsky/feed/like
   /models/app/bsky/feed/post
   /models/app/bsky/feed/postgate
   /models/app/bsky/feed/repost
   /models/app/bsky/feed/searchPosts
   /models/app/bsky/feed/searchPostsV2
   /models/app/bsky/feed/sendInteractions
   /models/app/bsky/feed/threadgate
