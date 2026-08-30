chat.bsky.convo
===============

Conversations, messages, and reactions.

.. automodule:: atproto_client.models.chat.bsky.convo
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` acceptConvo
      :link: /models/chat/bsky/convo/acceptConvo
      :link-type: doc

      Marks a conversation as accepted, so it is shown in the list of accepted convos instead on the request convos.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` addReaction
      :link: /models/chat/bsky/convo/addReaction
      :link-type: doc

      Adds an emoji reaction to a message.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/chat/bsky/convo/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deleteMessageForSelf
      :link: /models/chat/bsky/convo/deleteMessageForSelf
      :link-type: doc

      Marks a message as deleted for the viewer, so they won't see that message in future enumerations.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getConvo
      :link: /models/chat/bsky/convo/getConvo
      :link-type: doc

      Gets an existing conversation by its ID.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getConvoAvailability
      :link: /models/chat/bsky/convo/getConvoAvailability
      :link-type: doc

      Check whether the requester and the other members can start a 1-1 chat.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getConvoForMembers
      :link: /models/chat/bsky/convo/getConvoForMembers
      :link-type: doc

      Get or create a 1-1 conversation for the given members.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getConvoMembers
      :link: /models/chat/bsky/convo/getConvoMembers
      :link-type: doc

      Returns a paginated list of members from a conversation.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getLog
      :link: /models/chat/bsky/convo/getLog
      :link-type: doc

      Get log.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getMessages
      :link: /models/chat/bsky/convo/getMessages
      :link-type: doc

      Returns a page of messages from a conversation.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getUnreadCounts
      :link: /models/chat/bsky/convo/getUnreadCounts
      :link-type: doc

      Returns unread conversation counts for conversations that are unlocked, not muted, split by convo status.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` leaveConvo
      :link: /models/chat/bsky/convo/leaveConvo
      :link-type: doc

      Leaves a conversation (direct or group).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listConvoRequests
      :link: /models/chat/bsky/convo/listConvoRequests
      :link-type: doc

      Returns a page of incoming conversation requests for the user.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listConvos
      :link: /models/chat/bsky/convo/listConvos
      :link-type: doc

      Returns a page of conversations (direct or group) for the user.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` lockConvo
      :link: /models/chat/bsky/convo/lockConvo
      :link-type: doc

      Locks a group convo so no more content (messages, reactions) can be added to it.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` muteConvo
      :link: /models/chat/bsky/convo/muteConvo
      :link-type: doc

      Mutes a conversation, preventing notifications related to it.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` removeReaction
      :link: /models/chat/bsky/convo/removeReaction
      :link-type: doc

      Removes an emoji reaction from a message.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` sendMessage
      :link: /models/chat/bsky/convo/sendMessage
      :link-type: doc

      Sends a message to a conversation.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` sendMessageBatch
      :link: /models/chat/bsky/convo/sendMessageBatch
      :link-type: doc

      Sends a batch of messages to a conversation.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unlockConvo
      :link: /models/chat/bsky/convo/unlockConvo
      :link-type: doc

      Unlocks a group convo so it is able to receive new content.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unmuteConvo
      :link: /models/chat/bsky/convo/unmuteConvo
      :link-type: doc

      Unmutes a conversation, allowing notifications related to it.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateAllRead
      :link: /models/chat/bsky/convo/updateAllRead
      :link-type: doc

      Sets conversations from a user as read to the latest message, with filters.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateRead
      :link: /models/chat/bsky/convo/updateRead
      :link-type: doc

      Updates the read state of a conversation from, optionally specifying the last read message.

.. toctree::
   :hidden:
   :maxdepth: 1

   acceptConvo </models/chat/bsky/convo/acceptConvo>
   addReaction </models/chat/bsky/convo/addReaction>
   defs </models/chat/bsky/convo/defs>
   deleteMessageForSelf </models/chat/bsky/convo/deleteMessageForSelf>
   getConvo </models/chat/bsky/convo/getConvo>
   getConvoAvailability </models/chat/bsky/convo/getConvoAvailability>
   getConvoForMembers </models/chat/bsky/convo/getConvoForMembers>
   getConvoMembers </models/chat/bsky/convo/getConvoMembers>
   getLog </models/chat/bsky/convo/getLog>
   getMessages </models/chat/bsky/convo/getMessages>
   getUnreadCounts </models/chat/bsky/convo/getUnreadCounts>
   leaveConvo </models/chat/bsky/convo/leaveConvo>
   listConvoRequests </models/chat/bsky/convo/listConvoRequests>
   listConvos </models/chat/bsky/convo/listConvos>
   lockConvo </models/chat/bsky/convo/lockConvo>
   muteConvo </models/chat/bsky/convo/muteConvo>
   removeReaction </models/chat/bsky/convo/removeReaction>
   sendMessage </models/chat/bsky/convo/sendMessage>
   sendMessageBatch </models/chat/bsky/convo/sendMessageBatch>
   unlockConvo </models/chat/bsky/convo/unlockConvo>
   unmuteConvo </models/chat/bsky/convo/unmuteConvo>
   updateAllRead </models/chat/bsky/convo/updateAllRead>
   updateRead </models/chat/bsky/convo/updateRead>
