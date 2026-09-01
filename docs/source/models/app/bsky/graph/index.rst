app.bsky.graph
==============

Follows, blocks, mutes, lists, and starter packs.

.. automodule:: atproto_client.models.app.bsky.graph
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` block
      :link: /models/app/bsky/graph/block
      :link-type: doc

      Record declaring a 'block' relationship against another account.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/app/bsky/graph/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` follow
      :link: /models/app/bsky/graph/follow
      :link-type: doc

      Record declaring a social 'follow' relationship of another account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getActorStarterPacks
      :link: /models/app/bsky/graph/getActorStarterPacks
      :link-type: doc

      Get a list of starter packs created by the actor.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getBlocks
      :link: /models/app/bsky/graph/getBlocks
      :link-type: doc

      Enumerates which accounts the requesting account is currently blocking.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFollowers
      :link: /models/app/bsky/graph/getFollowers
      :link-type: doc

      Enumerates accounts which follow a specified account (actor).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getFollows
      :link: /models/app/bsky/graph/getFollows
      :link-type: doc

      Enumerates accounts which a specified account (actor) follows.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getKnownFollowers
      :link: /models/app/bsky/graph/getKnownFollowers
      :link-type: doc

      Enumerates accounts which follow a specified account (actor) and are followed by the viewer.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getList
      :link: /models/app/bsky/graph/getList
      :link-type: doc

      Gets a 'view' (with additional context) of a specified list.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getListBlocks
      :link: /models/app/bsky/graph/getListBlocks
      :link-type: doc

      Get mod lists that the requesting account (actor) is blocking.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getListMutes
      :link: /models/app/bsky/graph/getListMutes
      :link-type: doc

      Enumerates mod lists that the requesting account (actor) currently has muted.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getLists
      :link: /models/app/bsky/graph/getLists
      :link-type: doc

      Enumerates the lists created by a specified account (actor).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getListsWithMembership
      :link: /models/app/bsky/graph/getListsWithMembership
      :link-type: doc

      Enumerates the lists created by the session user, and includes membership information about ``actor`` in those lists.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getMutes
      :link: /models/app/bsky/graph/getMutes
      :link-type: doc

      Enumerates accounts that the requesting account (actor) currently has fully muted.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRelationships
      :link: /models/app/bsky/graph/getRelationships
      :link-type: doc

      Enumerates public relationships between one account, and a list of other accounts.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getStarterPack
      :link: /models/app/bsky/graph/getStarterPack
      :link-type: doc

      Gets a view of a starter pack.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getStarterPacks
      :link: /models/app/bsky/graph/getStarterPacks
      :link-type: doc

      Get views for a list of starter packs.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getStarterPacksWithMembership
      :link: /models/app/bsky/graph/getStarterPacksWithMembership
      :link-type: doc

      Enumerates the starter packs created by the session user, and includes membership information about ``actor`` in those starter packs.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSuggestedFollowsByActor
      :link: /models/app/bsky/graph/getSuggestedFollowsByActor
      :link-type: doc

      Enumerates follows similar to a given account (actor).

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` list
      :link: /models/app/bsky/graph/list
      :link-type: doc

      Record representing a list of accounts (actors).

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` listblock
      :link: /models/app/bsky/graph/listblock
      :link-type: doc

      Record representing a block relationship against an entire an entire list of accounts (actors).

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` listitem
      :link: /models/app/bsky/graph/listitem
      :link-type: doc

      Record representing an account's inclusion on a specific list.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` muteActor
      :link: /models/app/bsky/graph/muteActor
      :link-type: doc

      Creates a mute relationship for the specified account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` muteActorList
      :link: /models/app/bsky/graph/muteActorList
      :link-type: doc

      Creates a mute relationship for the specified list of accounts.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` muteThread
      :link: /models/app/bsky/graph/muteThread
      :link-type: doc

      Mutes a thread preventing notifications from the thread and any of its children.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` referencelistoptout
      :link: /models/app/bsky/graph/referencelistoptout
      :link-type: doc

      Record requesting that its author be omitted from the public presentation of a reference list.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` searchStarterPacks
      :link: /models/app/bsky/graph/searchStarterPacks
      :link-type: doc

      Find starter packs matching search criteria.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` searchStarterPacksV2
      :link: /models/app/bsky/graph/searchStarterPacksV2
      :link-type: doc

      Find starter packs matching search criteria.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` starterpack
      :link: /models/app/bsky/graph/starterpack
      :link-type: doc

      Record defining a starter pack of actors and feeds for new users.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unmuteActor
      :link: /models/app/bsky/graph/unmuteActor
      :link-type: doc

      Unmutes the specified account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unmuteActorList
      :link: /models/app/bsky/graph/unmuteActorList
      :link-type: doc

      Unmutes the specified list of accounts.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unmuteThread
      :link: /models/app/bsky/graph/unmuteThread
      :link-type: doc

      Unmutes the specified thread.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` verification
      :link: /models/app/bsky/graph/verification
      :link-type: doc

      Record declaring a verification relationship between two accounts.

.. toctree::
   :hidden:
   :maxdepth: 1

   block </models/app/bsky/graph/block>
   defs </models/app/bsky/graph/defs>
   follow </models/app/bsky/graph/follow>
   getActorStarterPacks </models/app/bsky/graph/getActorStarterPacks>
   getBlocks </models/app/bsky/graph/getBlocks>
   getFollowers </models/app/bsky/graph/getFollowers>
   getFollows </models/app/bsky/graph/getFollows>
   getKnownFollowers </models/app/bsky/graph/getKnownFollowers>
   getList </models/app/bsky/graph/getList>
   getListBlocks </models/app/bsky/graph/getListBlocks>
   getListMutes </models/app/bsky/graph/getListMutes>
   getLists </models/app/bsky/graph/getLists>
   getListsWithMembership </models/app/bsky/graph/getListsWithMembership>
   getMutes </models/app/bsky/graph/getMutes>
   getRelationships </models/app/bsky/graph/getRelationships>
   getStarterPack </models/app/bsky/graph/getStarterPack>
   getStarterPacks </models/app/bsky/graph/getStarterPacks>
   getStarterPacksWithMembership </models/app/bsky/graph/getStarterPacksWithMembership>
   getSuggestedFollowsByActor </models/app/bsky/graph/getSuggestedFollowsByActor>
   list </models/app/bsky/graph/list>
   listblock </models/app/bsky/graph/listblock>
   listitem </models/app/bsky/graph/listitem>
   muteActor </models/app/bsky/graph/muteActor>
   muteActorList </models/app/bsky/graph/muteActorList>
   muteThread </models/app/bsky/graph/muteThread>
   referencelistoptout </models/app/bsky/graph/referencelistoptout>
   searchStarterPacks </models/app/bsky/graph/searchStarterPacks>
   searchStarterPacksV2 </models/app/bsky/graph/searchStarterPacksV2>
   starterpack </models/app/bsky/graph/starterpack>
   unmuteActor </models/app/bsky/graph/unmuteActor>
   unmuteActorList </models/app/bsky/graph/unmuteActorList>
   unmuteThread </models/app/bsky/graph/unmuteThread>
   verification </models/app/bsky/graph/verification>
