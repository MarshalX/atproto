app.bsky.unspecced.getPostThreadOtherV2
=======================================

(NOTE: this endpoint is under development and WILL change without notice. Don't use it until it is moved out of ``unspecced`` or your application WILL break) Get additional posts under a thread e.g. replies hidden by threadgate. Based on an anchor post at any depth of the tree, returns top-level replies below that anchor. It does not include ancestors nor the anchor itself. This should be called after exhausting ``app.bsky.unspecced.getPostThreadV2``. Does not require auth, but additional metadata and filtering will be applied for authed requests.

.. automodule:: atproto_client.models.app.bsky.unspecced.get_post_thread_other_v2
   :members:
   :show-inheritance:
   :undoc-members:
