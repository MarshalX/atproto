network.bsky.jetstream
======================

Jetstream: event stream, archive segments, and imports.

.. automodule:: atproto_client.models.network.bsky.jetstream
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getBlock
      :link: /models/network/bsky/jetstream/getBlock
      :link-type: doc

      Download a single block within a sealed segment file by index.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getImportStatus
      :link: /models/network/bsky/jetstream/getImportStatus
      :link-type: doc

      Report the status of a timestamp-import job: lifecycle state, current phase, per-phase progress, and (on completion) the parse/mutation totals.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSegment
      :link: /models/network/bsky/jetstream/getSegment
      :link-type: doc

      Download a sealed segment file by name.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getZstdDictionary
      :link: /models/network/bsky/jetstream/getZstdDictionary
      :link-type: doc

      Download the zstd dictionary used by the network.bsky.jetstream.subscribeEvents stream's optional compression scheme.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` importTimestamps
      :link: /models/network/bsky/jetstream/importTimestamps
      :link-type: doc

      Submit a timestamp-import job.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listSegments
      :link: /models/network/bsky/jetstream/listSegments
      :link-type: doc

      Enumerate sealed segment files available for download, in ascending index order.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` planSnapshot
      :link: /models/network/bsky/jetstream/planSnapshot
      :link-type: doc

      Build a download plan for the desired data pattern.

   .. grid-item-card:: :octicon:`broadcast;1em;sd-mr-1` subscribeEvents
      :link: /models/network/bsky/jetstream/subscribeEvents
      :link-type: doc

      Stream every archived and live Jetstream event in seq order, framed per the xrpc.v1.json subprotocol.

.. toctree::
   :hidden:
   :maxdepth: 1

   getBlock </models/network/bsky/jetstream/getBlock>
   getImportStatus </models/network/bsky/jetstream/getImportStatus>
   getSegment </models/network/bsky/jetstream/getSegment>
   getZstdDictionary </models/network/bsky/jetstream/getZstdDictionary>
   importTimestamps </models/network/bsky/jetstream/importTimestamps>
   listSegments </models/network/bsky/jetstream/listSegments>
   planSnapshot </models/network/bsky/jetstream/planSnapshot>
   subscribeEvents </models/network/bsky/jetstream/subscribeEvents>
