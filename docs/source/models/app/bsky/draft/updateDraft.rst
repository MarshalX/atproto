app.bsky.draft.updateDraft
==========================

Updates a draft using private storage (stash). If the draft ID points to a non-existing ID, the update will be silently ignored. This is done because updates don't enforce draft limit, so it accepts all writes, but will ignore invalid ones. Requires authentication.

.. automodule:: atproto_client.models.app.bsky.draft.update_draft
   :members:
   :show-inheritance:
   :undoc-members:
