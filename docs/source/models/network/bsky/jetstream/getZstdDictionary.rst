network.bsky.jetstream.getZstdDictionary
========================================

Download the zstd dictionary used by the network.bsky.jetstream.subscribeEvents stream's optional compression scheme. The dictionary is requested by its zstd dictionary ID (the same ID embedded in every compressed frame's header); a client that wants compressed frames first fetches the server's current dictionary, then opts in on the websocket with zstdDictionary=<id>. The response is a raw zstd structured dictionary (RFC 8878 section 5), immutable for a given ID and CDN-cacheable. Servers may retire old dictionaries after retraining; a client holding a retired ID re-fetches without an id parameter to obtain the current one.

.. automodule:: atproto_client.models.network.bsky.jetstream.get_zstd_dictionary
   :members:
   :show-inheritance:
   :undoc-members:
