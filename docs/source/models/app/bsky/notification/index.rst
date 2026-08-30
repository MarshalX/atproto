app.bsky.notification
=====================

Notifications, preferences, and push registration.

.. automodule:: atproto_client.models.app.bsky.notification
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` declaration
      :link: /models/app/bsky/notification/declaration
      :link-type: doc

      A declaration of the user's choices related to notifications that can be produced by them.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/app/bsky/notification/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getPreferences
      :link: /models/app/bsky/notification/getPreferences
      :link-type: doc

      Get notification-related preferences for an account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getUnreadCount
      :link: /models/app/bsky/notification/getUnreadCount
      :link-type: doc

      Count the number of unread notifications for the requesting account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listActivitySubscriptions
      :link: /models/app/bsky/notification/listActivitySubscriptions
      :link-type: doc

      Enumerate all accounts to which the requesting account is subscribed to receive notifications for.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listNotifications
      :link: /models/app/bsky/notification/listNotifications
      :link-type: doc

      Enumerate notifications for the requesting account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` putActivitySubscription
      :link: /models/app/bsky/notification/putActivitySubscription
      :link-type: doc

      Puts an activity subscription entry.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` putPreferences
      :link: /models/app/bsky/notification/putPreferences
      :link-type: doc

      Set notification-related preferences for an account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` putPreferencesV2
      :link: /models/app/bsky/notification/putPreferencesV2
      :link-type: doc

      Set notification-related preferences for an account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` registerPush
      :link: /models/app/bsky/notification/registerPush
      :link-type: doc

      Register to receive push notifications, via a specified service, for the requesting account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` unregisterPush
      :link: /models/app/bsky/notification/unregisterPush
      :link-type: doc

      The inverse of registerPush - inform a specified service that push notifications should no longer be sent to the given token for the requesting account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateSeen
      :link: /models/app/bsky/notification/updateSeen
      :link-type: doc

      Notify server that the requesting account has seen notifications.

.. toctree::
   :hidden:
   :maxdepth: 1

   /models/app/bsky/notification/declaration
   /models/app/bsky/notification/defs
   /models/app/bsky/notification/getPreferences
   /models/app/bsky/notification/getUnreadCount
   /models/app/bsky/notification/listActivitySubscriptions
   /models/app/bsky/notification/listNotifications
   /models/app/bsky/notification/putActivitySubscription
   /models/app/bsky/notification/putPreferences
   /models/app/bsky/notification/putPreferencesV2
   /models/app/bsky/notification/registerPush
   /models/app/bsky/notification/unregisterPush
   /models/app/bsky/notification/updateSeen
