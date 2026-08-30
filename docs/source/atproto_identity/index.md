# Identity (DID and Handle resolvers)

The AT Protocol has two identifiers: handles, which are DNS names, and DIDs, which are stable W3C identifiers. This package resolves between them, fetches DID documents, and caches the results.

[IdResolver](#atproto_identity.resolver.IdResolver) / [AsyncIdResolver](#atproto_identity.resolver.AsyncIdResolver)
: The entry point. `.handle` resolves a handle to a DID over DNS and HTTP; `.did` resolves a DID to its document over the PLC directory or HTTP.

```python
from atproto import IdResolver  # AsyncIdResolver for async

resolver = IdResolver()
did = resolver.handle.resolve('test.marshal.dev')
did_doc = resolver.did.resolve(did)
```

:::{tip}
For the full story, covering `resolve` versus `ensure_resolve`, `did:web` versus `did:plc`, writing your own cache, and pulling the signing key out of a DID document, see the [Identity guide](../guides/identity.md).
:::

A DID document is modelled by [DidDocument](#atproto_core.did_doc.did_doc.DidDocument) in [atproto_core](../atproto_core/index.md).

```{eval-rst}
.. automodule:: atproto_identity
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

id_resolver
handle_resolver
did_resolver
cache
atproto_data
```
