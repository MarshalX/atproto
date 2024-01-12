Identity (DID and Handle resolvers)
===================================

Check out what is a DID Document in the :doc:`../atproto_core/did_doc`.

AT Protocol uses two identifiers: DID and Handle. Handles are DNS names while DIDs are an emerging W3C standard which act as secure & stable IDs.

The AT Protocol Identity module provides a way to resolve DIDs and Handles. It also provides a way to cache the results of these resolutions.

Under the hood, the Identity module resolves Handlers using DNS and HTTP. It resolves DIDs using PLC directory and HTTP.

Typically, you don't need to care about the details of how the Identity module works. You can simply use the ``IdResolver`` class to resolve DIDs and Handles:

..  code-block:: python

    from atproto import IdResolver  # for async use AsyncIdResolver

    resolver = IdResolver()
    did = resolver.handle.resolve('test.marshal.dev')
    did_doc = resolver.did.resolve(did)

    print(did)
    print(did_doc)


Learn how to use cache to speed up the resolution process in the :doc:`cache` section.

.. automodule:: atproto_identity.resolver
   :members:
   :undoc-members:
   :inherited-members:

Submodules
----------

.. toctree::
   :maxdepth: 4

   id_resolver
   handle_resolver
   did_resolver
   cache
   atproto_data
