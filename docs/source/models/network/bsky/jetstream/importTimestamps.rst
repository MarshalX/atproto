network.bsky.jetstream.importTimestamps
=======================================

Submit a timestamp-import job. The referenced CSV is staged server-local out-of-band and named by a path confined to the server's configured import directory (paths escaping it via .. or a symlink are rejected). The job runs asynchronously and shares the segment-rewrite lock with delete-compaction, so only one import runs at a time; a concurrent submit is rejected. Bearer-token gated: without a configured token the endpoint always returns 401.

.. automodule:: atproto_client.models.network.bsky.jetstream.import_timestamps
   :members:
   :show-inheritance:
   :undoc-members:
