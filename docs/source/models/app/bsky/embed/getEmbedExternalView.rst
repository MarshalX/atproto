app.bsky.embed.getEmbedExternalView
===================================

Resolve one AT-URI record into the data needed to render an enhanced external embed. The records are validated against the requested ``url`` before any view is built. When validation passes, returns ``data``, ``associatedRefs`` (strongRefs to embed into a post's external.associatedRefs) and the raw ``associatedRecords``, plus a legacy ``view`` for Standard.site records only. When validation fails, only ``unverifiedAssociatedRefs`` and ``unverifiedAssociatedRecords`` are returned and no view or data is built. The response is empty (``{}``) when no record URI was usable or the record could not be resolved; clients should fall back to their own link-card rendering in that case and skip writing strongRefs to the post.

.. automodule:: atproto_client.models.app.bsky.embed.get_embed_external_view
   :members:
   :show-inheritance:
   :undoc-members:
