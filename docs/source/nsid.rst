NSID (NameSpaced ID)
====================

NameSpaced IDs (NSIDs) are used throughout ATP to identify methods, records types, and other semantic information.

NSIDs use Reverse Domain-Name Notation with the additional constraint that the segments prior to the final segment must map to a valid domain name. For instance, the owner of example.com could use the ID of com.example.foo but could not use com.example.foo.bar unless they also control foo.example.com. These rules are to ensure that schemas are globally unique, have a clear authority mapping (to a registered domain), and can potentially be resolved by request.

More info: https://atproto.com/specs/nsid

.. automodule:: atproto_core.nsid
   :members:
   :undoc-members:
   :show-inheritance: