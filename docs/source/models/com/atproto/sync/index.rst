com.atproto.sync
================

Repository sync: firehose, blocks, blobs, and checkouts.

.. automodule:: atproto_client.models.com.atproto.sync
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/com/atproto/sync/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getBlob
      :link: /models/com/atproto/sync/getBlob
      :link-type: doc

      Get a blob associated with a given account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getBlocks
      :link: /models/com/atproto/sync/getBlocks
      :link-type: doc

      Get data blocks from a given repo, by CID.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getCheckout
      :link: /models/com/atproto/sync/getCheckout
      :link-type: doc

      DEPRECATED - please use com.atproto.sync.getRepo instead

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getHead
      :link: /models/com/atproto/sync/getHead
      :link-type: doc

      DEPRECATED - please use com.atproto.sync.getLatestCommit instead

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getHostStatus
      :link: /models/com/atproto/sync/getHostStatus
      :link-type: doc

      Returns information about a specified upstream host, as consumed by the server.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getLatestCommit
      :link: /models/com/atproto/sync/getLatestCommit
      :link-type: doc

      Get the current commit CID & revision of the specified repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRecord
      :link: /models/com/atproto/sync/getRecord
      :link-type: doc

      Get data blocks needed to prove the existence or non-existence of record in the current version of repo.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRepo
      :link: /models/com/atproto/sync/getRepo
      :link-type: doc

      Download a repository export as CAR file.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getRepoStatus
      :link: /models/com/atproto/sync/getRepoStatus
      :link-type: doc

      Get the hosting status for a repository, on this server.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listBlobs
      :link: /models/com/atproto/sync/listBlobs
      :link-type: doc

      List blob CIDs for an account, since some repo revision.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listHosts
      :link: /models/com/atproto/sync/listHosts
      :link-type: doc

      Enumerates upstream hosts (eg, PDS or relay instances) that this service consumes from.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listRepos
      :link: /models/com/atproto/sync/listRepos
      :link-type: doc

      Enumerates all the DID, rev, and commit CID for all repos hosted by this service.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listReposByCollection
      :link: /models/com/atproto/sync/listReposByCollection
      :link-type: doc

      Enumerates all the DIDs which have records with the given collection NSID.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` notifyOfUpdate
      :link: /models/com/atproto/sync/notifyOfUpdate
      :link-type: doc

      Notify a crawling service of a recent update, and that crawling should resume.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestCrawl
      :link: /models/com/atproto/sync/requestCrawl
      :link-type: doc

      Request a service to persistently crawl hosted repos.

   .. grid-item-card:: :octicon:`broadcast;1em;sd-mr-1` subscribeRepos
      :link: /models/com/atproto/sync/subscribeRepos
      :link-type: doc

      Repository event stream, aka Firehose endpoint.

.. toctree::
   :hidden:
   :maxdepth: 1

   defs </models/com/atproto/sync/defs>
   getBlob </models/com/atproto/sync/getBlob>
   getBlocks </models/com/atproto/sync/getBlocks>
   getCheckout </models/com/atproto/sync/getCheckout>
   getHead </models/com/atproto/sync/getHead>
   getHostStatus </models/com/atproto/sync/getHostStatus>
   getLatestCommit </models/com/atproto/sync/getLatestCommit>
   getRecord </models/com/atproto/sync/getRecord>
   getRepo </models/com/atproto/sync/getRepo>
   getRepoStatus </models/com/atproto/sync/getRepoStatus>
   listBlobs </models/com/atproto/sync/listBlobs>
   listHosts </models/com/atproto/sync/listHosts>
   listRepos </models/com/atproto/sync/listRepos>
   listReposByCollection </models/com/atproto/sync/listReposByCollection>
   notifyOfUpdate </models/com/atproto/sync/notifyOfUpdate>
   requestCrawl </models/com/atproto/sync/requestCrawl>
   subscribeRepos </models/com/atproto/sync/subscribeRepos>
