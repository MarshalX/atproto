app.bsky.unspecced.getAtmosphereRecordView
==========================================

Get a hydrated view of one Atmosphere record. Requires authentication. Without ``cid`` the latest version of the record is returned; with ``cid`` exactly that version is returned, never another. Dependencies of the record are always latest. Returns an empty object when the record is missing or not visible. When the record is visible but cannot produce a view, only the associations are returned.

.. automodule:: atproto_client.models.app.bsky.unspecced.get_atmosphere_record_view
   :members:
   :show-inheritance:
   :undoc-members:
