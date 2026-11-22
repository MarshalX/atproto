com.atproto.space
=================

Spaces of permissioned data: records, policies, credentials, and sync.

.. automodule:: atproto_client.models.com.atproto.space
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` applyWrites
      :link: /models/com/atproto/space/applyWrites
      :link-type: doc

      Apply a batch transaction of creates, updates, and deletes to a space repo.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` authorizeSpaceSync
      :link: /models/com/atproto/space/authorizeSpaceSync
      :link-type: doc

      Authorize syncing a space, returning a new credential for reading data across it and the space's current revision, and optionally registering for notifications of updates to it.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` clearRecords
      :link: /models/com/atproto/space/clearRecords
      :link-type: doc

      Delete all records in the authenticated account's space repo.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` confirmRegistration
      :link: /models/com/atproto/space/confirmRegistration
      :link-type: doc

      Confirm a new notification registration.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createRecord
      :link: /models/com/atproto/space/createRecord
      :link-type: doc

      Create a single new record in a space repo.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createSpace
      :link: /models/com/atproto/space/createSpace
      :link-type: doc

      Create a new space, with the authenticated account as its authority.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/com/atproto/space/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deleteRecord
      :link: /models/com/atproto/space/deleteRecord
      :link-type: doc

      Delete a record from a space repo, or ensure it doesn't exist.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deleteSpace
      :link: /models/com/atproto/space/deleteSpace
      :link-type: doc

      Delete a space, along with the authority's space repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` exportSpaceMeta
      :link: /models/com/atproto/space/exportSpaceMeta
      :link-type: doc

      Export a space's state, such as its policy and member list, as a STAR file for account migration.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getBlob
      :link: /models/com/atproto/space/getBlob
      :link-type: doc

      Get a blob referenced by a record in a space repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getDelegationToken
      :link: /models/com/atproto/space/getDelegationToken
      :link-type: doc

      Get a delegation token for a space, to exchange with the space host for a space credential.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getLatestCommit
      :link: /models/com/atproto/space/getLatestCommit
      :link-type: doc

      Get the current commit of a space repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRecord
      :link: /models/com/atproto/space/getRecord
      :link-type: doc

      Get a single record from a space repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRepo
      :link: /models/com/atproto/space/getRepo
      :link-type: doc

      Download a space repo as a STAR file.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSpace
      :link: /models/com/atproto/space/getSpace
      :link-type: doc

      Get a space and its policy.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` importRepo
      :link: /models/com/atproto/space/importRepo
      :link-type: doc

      Import the authenticated account's space repo from a STAR file, for account migration.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` importSpaceMeta
      :link: /models/com/atproto/space/importSpaceMeta
      :link-type: doc

      Import a space's state from an archive produced by exportSpaceMeta, for account migration.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listBlobs
      :link: /models/com/atproto/space/listBlobs
      :link-type: doc

      List blob CIDs referenced by records in a space repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listRecords
      :link: /models/com/atproto/space/listRecords
      :link-type: doc

      List records in a space repo, optionally filtered by collection.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listRepoOps
      :link: /models/com/atproto/space/listRepoOps
      :link-type: doc

      List operations on a space repo after a given revision.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listSpaces
      :link: /models/com/atproto/space/listSpaces
      :link-type: doc

      List spaces that the authenticated account has written to or is the authority for.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listWriters
      :link: /models/com/atproto/space/listWriters
      :link-type: doc

      List the repos in a space's writer set, with the latest known state of each: its current revision, or its removal from the writer set.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` notifyCredentialsRevoked
      :link: /models/com/atproto/space/notifyCredentialsRevoked
      :link-type: doc

      Notify a repo host that space credentials have been revoked.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` notifyRepoUpdate
      :link: /models/com/atproto/space/notifyRepoUpdate
      :link-type: doc

      Notify the space host that a space repo has been updated.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` notifySpaceUpdate
      :link: /models/com/atproto/space/notifySpaceUpdate
      :link-type: doc

      Notify a syncing service of an update to a space.

   .. grid-item-card:: :octicon:`note;1em;sd-mr-1` policy
      :link: /models/com/atproto/space/policy
      :link-type: doc

      A published copy of a space's policy.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` putRecord
      :link: /models/com/atproto/space/putRecord
      :link-type: doc

      Write a record in a space repo, creating or updating it as needed.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` removeWriter
      :link: /models/com/atproto/space/removeWriter
      :link-type: doc

      Remove an account from a space's writer set, as returned by listWriters.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateSpace
      :link: /models/com/atproto/space/updateSpace
      :link-type: doc

      Replace the policy of a space.

.. toctree::
   :hidden:
   :maxdepth: 1

   applyWrites </models/com/atproto/space/applyWrites>
   authorizeSpaceSync </models/com/atproto/space/authorizeSpaceSync>
   clearRecords </models/com/atproto/space/clearRecords>
   confirmRegistration </models/com/atproto/space/confirmRegistration>
   createRecord </models/com/atproto/space/createRecord>
   createSpace </models/com/atproto/space/createSpace>
   defs </models/com/atproto/space/defs>
   deleteRecord </models/com/atproto/space/deleteRecord>
   deleteSpace </models/com/atproto/space/deleteSpace>
   exportSpaceMeta </models/com/atproto/space/exportSpaceMeta>
   getBlob </models/com/atproto/space/getBlob>
   getDelegationToken </models/com/atproto/space/getDelegationToken>
   getLatestCommit </models/com/atproto/space/getLatestCommit>
   getRecord </models/com/atproto/space/getRecord>
   getRepo </models/com/atproto/space/getRepo>
   getSpace </models/com/atproto/space/getSpace>
   importRepo </models/com/atproto/space/importRepo>
   importSpaceMeta </models/com/atproto/space/importSpaceMeta>
   listBlobs </models/com/atproto/space/listBlobs>
   listRecords </models/com/atproto/space/listRecords>
   listRepoOps </models/com/atproto/space/listRepoOps>
   listSpaces </models/com/atproto/space/listSpaces>
   listWriters </models/com/atproto/space/listWriters>
   notifyCredentialsRevoked </models/com/atproto/space/notifyCredentialsRevoked>
   notifyRepoUpdate </models/com/atproto/space/notifyRepoUpdate>
   notifySpaceUpdate </models/com/atproto/space/notifySpaceUpdate>
   policy </models/com/atproto/space/policy>
   putRecord </models/com/atproto/space/putRecord>
   removeWriter </models/com/atproto/space/removeWriter>
   updateSpace </models/com/atproto/space/updateSpace>
