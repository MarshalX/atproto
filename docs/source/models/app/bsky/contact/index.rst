app.bsky.contact
================

Contact discovery between actors.

.. automodule:: atproto_client.models.app.bsky.contact
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/app/bsky/contact/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` dismissMatch
      :link: /models/app/bsky/contact/dismissMatch
      :link-type: doc

      Removes a match that was found via contact import.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getMatches
      :link: /models/app/bsky/contact/getMatches
      :link-type: doc

      Returns the matched contacts (contacts that were mutually imported).

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSyncStatus
      :link: /models/app/bsky/contact/getSyncStatus
      :link-type: doc

      Gets the user's current contact import status.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` importContacts
      :link: /models/app/bsky/contact/importContacts
      :link-type: doc

      Import contacts for securely matching with other users.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` removeData
      :link: /models/app/bsky/contact/removeData
      :link-type: doc

      Removes all stored hashes used for contact matching, existing matches, and sync status.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` sendNotification
      :link: /models/app/bsky/contact/sendNotification
      :link-type: doc

      System endpoint to send notifications related to contact imports.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` startPhoneVerification
      :link: /models/app/bsky/contact/startPhoneVerification
      :link-type: doc

      Starts a phone verification flow.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` verifyPhone
      :link: /models/app/bsky/contact/verifyPhone
      :link-type: doc

      Verifies control over a phone number with a code received via SMS and starts a contact import session.

.. toctree::
   :hidden:
   :maxdepth: 1

   /models/app/bsky/contact/defs
   /models/app/bsky/contact/dismissMatch
   /models/app/bsky/contact/getMatches
   /models/app/bsky/contact/getSyncStatus
   /models/app/bsky/contact/importContacts
   /models/app/bsky/contact/removeData
   /models/app/bsky/contact/sendNotification
   /models/app/bsky/contact/startPhoneVerification
   /models/app/bsky/contact/verifyPhone
