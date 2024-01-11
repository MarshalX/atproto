Cache
=====

Cache could be used to store previously resolved DID Documents. SDK provides ``DidInMemoryCache`` and ``DidBaseCache`` classes.

``DidInMemoryCache`` is a simple implementation of ``DidBaseCache`` that stores data in memory. Feel free to use it as real cache or as a reference implementation.

``DidBaseCache`` is an abstract class that could be used to implement custom cache. Please note that there is 2 base classes. One for synchronous and another for asynchronous cache.

Here is an example of how to use ``DidInMemoryCache`` with ``IdResolver``:

.. code-block:: python

    from atproto import DidInMemoryCache, IdResolver  # for async use AsyncDidInMemoryCache and AsyncIdResolver

    cache = DidInMemoryCache()
    resolver = IdResolver(cache=cache)
    did_doc = resolver.did.resolve('did:web:feed.atproto.blue')

    # Now did_document is cached and could be retrieved without network request
    did_doc = resolver.did.resolve('did:web:feed.atproto.blue')

    # Clear cache
    cache.clear()

    # Now did_document is not cached and will be retrieved with network request
    did_doc = resolver.did.resolve('did:web:feed.atproto.blue')


.. automodule:: atproto_identity.cache.in_memory_cache
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: atproto_identity.cache.base_cache
   :members:
   :undoc-members:
   :show-inheritance:
