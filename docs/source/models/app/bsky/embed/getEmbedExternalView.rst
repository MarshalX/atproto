app.bsky.embed.getEmbedExternalView
===================================

Resolve one or more AT-URIs into the data needed to render an enhanced external embed. Returns ``associatedRefs`` (strongRefs to embed into a post's external.associatedRefs), the raw ``associatedRecords``, and a hydrated ``view``. The response is empty (``{}``) when no records were resolvable, or when validation determined the resolved records don't actually back the requested URL; clients should fall back to their own link-card rendering in that case and skip writing strongRefs to the post.

.. automodule:: atproto_client.models.app.bsky.embed.get_embed_external_view
   :members:
   :show-inheritance:
   :undoc-members:
