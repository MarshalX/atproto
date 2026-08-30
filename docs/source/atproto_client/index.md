# Client (API)

The reference for `atproto_client`: the clients, the generated namespaces, and the utilities around them. If you are looking for how to *do* something rather than for a signature, the [guides](../guides/index.md) are the better entry point.

There are three layers here, and you can move between them freely:

[Client](#atproto_client.client.client.Client) / [AsyncClient](#atproto_client.client.async_client.AsyncClient)
: The high-level, hand-written layer. `send_post`, `like`, `get_timeline`, `login`, and the session and header machinery. Covers what people do most often, and nothing more. See [Posting](../guides/posting.md) and [Reading content](../guides/reading.md).

Namespaces
: The generated layer, and the real API. Every lexicon method on the network, reachable by its NSID: `client.com.atproto.repo.create_record(...)`, `client.app.bsky.graph.get_follows(...)`. The high-level client is built out of these. See [Records and repositories](../guides/records-and-repos.md).

[ClientRaw](#atproto_client.client.raw.ClientRaw)
: The namespace roots with no convenience layer at all, for when you want nothing but XRPC.

Underneath all three sits [Request](#atproto_client.request.Request), which wraps `httpx` and is where timeouts, proxies, retries, and headers are configured. See [HTTP and transport](../guides/http-and-transport.md).

```{eval-rst}
.. automodule:: atproto_client
   :members:
   :undoc-members:
   :inherited-members:
   :no-index:
```

## Submodules

```{toctree}
:maxdepth: 4

clients
namespace
utils/index
```
