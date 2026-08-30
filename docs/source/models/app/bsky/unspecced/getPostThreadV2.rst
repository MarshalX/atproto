app.bsky.unspecced.getPostThreadV2
==================================

(NOTE: this endpoint is under development and WILL change without notice. Don't use it until it is moved out of ``unspecced`` or your application WILL break) Get posts in a thread. It is based in an anchor post at any depth of the tree, and returns posts above it (recursively resolving the parent, without further branching to their replies) and below it (recursive replies, with branching to their replies). Does not require auth, but additional metadata and filtering will be applied for authed requests.

.. automodule:: atproto_client.models.app.bsky.unspecced.get_post_thread_v2
   :members:
   :show-inheritance:
   :undoc-members:
