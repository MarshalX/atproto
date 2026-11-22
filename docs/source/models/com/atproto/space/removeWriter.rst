com.atproto.space.removeWriter
==============================

Remove an account from a space's writer set, as returned by listWriters. The removal is sent to registered syncers. The account is added back if it makes another authorized write to the space. Does nothing if the account is not in the writer set. Requires auth as the space authority, implemented by PDS.

.. automodule:: atproto_client.models.com.atproto.space.remove_writer
   :members:
   :show-inheritance:
   :undoc-members:
