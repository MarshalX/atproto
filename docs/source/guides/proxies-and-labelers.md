# Proxies and labelers

Some services are not reached directly. You send the request to your PDS with a header naming the service you actually want, and the PDS forwards it, signing a service token on your behalf. That is how direct messages and moderation tooling work: one client, one session, different destinations.

Two headers do this, and the SDK wraps both.

The protocol side is documented at [bsky.network/docs/bluesky-api/request-proxying](https://bsky.network/docs/bluesky-api/request-proxying).

## Proxying

[with_proxy](#atproto_client.client.client.Client.with_proxy) sets the `atproto-proxy` header, whose value is `<did>#<service_type>`: the DID of the service, and the id of the service entry in that DID's document.

```python
ozone = client.with_proxy('atproto_labeler', 'did:plc:ar7c4by46qjdydhdevvrndac')
ozone.tools.ozone.moderation.get_repo({'did': 'did:plc:...'})
```

`service_type` also accepts the `AtprotoServiceType` enum, which names the two service types the SDK knows about:

`AtprotoServiceType.ATPROTO_LABELER` (`'atproto_labeler'`)
: A labeler service, which also serves the Ozone moderation endpoints under `tools.ozone`.

`AtprotoServiceType.BSKY_CHAT` (`'bsky_chat'`)
: The Bluesky chat service.

The DID must start with `did:`. Anything else raises [AtProtocolError](#atproto_core.exceptions.AtProtocolError) immediately, before any request.

### The chat shortcut

Direct messages always go through the same service, so there is a wrapper:

```python
dm_client = client.with_bsky_chat_proxy()
dm_client.chat.bsky.convo.list_convos()
```

[with_bsky_chat_proxy](#atproto_client.client.client.Client.with_bsky_chat_proxy) is exactly `with_proxy(AtprotoServiceType.BSKY_CHAT, Client.BSKY_CHAT_DID)`, where `BSKY_CHAT_DID` is the class constant `'did:web:api.bsky.chat'`. Every `chat.bsky.*` call needs it. See [Direct messages](direct-messages.md).

## Labelers

Labels are not applied by the AppView on its own initiative. The client declares which labeler services it subscribes to, per request, and the AppView hydrates labels from those services into the response.

[with_labelers](#atproto_client.client.client.Client.with_labelers) takes a list of DIDs and sets the `atproto-accept-labelers` header:

```python
labeled = client.with_labelers(['did:plc:ar7c4by46qjdydhdevvrndac'])
profile = labeled.get_profile('bsky.app')
for label in profile.labels or []:
    print(label.val, label.src)
```

[with_bsky_labeler](#atproto_client.client.client.Client.with_bsky_labeler) is the shortcut for Bluesky's own moderation service, `Client.BSKY_LABELER_DID` (`'did:plc:ar7c4by46qjdydhdevvrndac'`).

:::{note}
Each DID is emitted with a `;redact` suffix, as in `did:plc:abc;redact`, which tells the AppView the client honours takedown labels from that labeler and wants the content removed rather than flagged. The SDK always sends `;redact`; there is no option to opt out of it.

Entries that do not start with `did:` are silently dropped from the list rather than raising.
:::

```{literalinclude} ../../../examples/advanced_usage/proxy_and_labelers.py
:language: python
:caption: examples/advanced_usage/proxy_and_labelers.py
```

## Cloning

Both `with_*` methods call [clone](#atproto_client.client.client.Client.clone) and configure the copy. The client you called them on is unchanged, so a proxied client for chat and a plain client for everything else can coexist, and you do not have to unset a header when you are done.

What a clone shares with its original:

- **The session.** Same `Session` object, same access and refresh tokens.
- **The session dispatcher**, and with it every `on_session_change` callback.
- **`me`**, the profile fetched at login.

What a clone copies:

- **The request's additional headers.** A fresh dict, so configuring the clone does not touch the original's headers.
- **The additional-header sources.** The list of callbacks is copied; the callbacks themselves are shared.
- **The configuration of the underlying `httpx` client.** Every keyword argument the original [Request](#atproto_client.request.Request) was constructed with, so a timeout, transport or proxy you set carries over.

What a clone does **not** share is the `httpx` client itself. Each one opens its own connection pool, so `close()` it separately. See [HTTP and transport](http-and-transport.md).

Sharing the session is the important half. A token refresh triggered by any one of the clones updates the session all of them are using, and fires the callbacks registered on any of them. Logging in once and fanning out into several proxied clients is the intended pattern.

Because the session lives in the shared dispatcher rather than on the client, the order does not matter: a clone taken *before* `login()` picks up the session the original creates later, and authenticates from that point on.

:::{attention}
A clone inherits the base URL as it stands at the moment you clone. Login repoints the client at the PDS discovered in the DID document, so a clone taken before login keeps the URL you constructed the client with. Cloning after login is still the simpler thing to do. See [Authentication](authentication.md).
:::

## Headers, and who wins

Every request's headers are assembled by [get_headers](#atproto_client.request.RequestBase.get_headers) in a fixed order, each layer overriding the last. Comparison is case-insensitive, so `Atproto-Proxy` and `atproto-proxy` are the same header.

1. **Mandatory headers.** Currently just `User-Agent`, set to `atproto/<version> Python SDK (atproto.blue)`. It is applied first, which means it is the one thing anything else can override: set your own `User-Agent` and it wins.
2. **Additional headers**, set by [set_additional_headers](#atproto_client.request.RequestBase.set_additional_headers) or [add_additional_header](#atproto_client.request.RequestBase.add_additional_header). This is where `configure_proxy_header` and `configure_labelers_header` write.
3. **Header sources**, registered with [add_additional_headers_source](#atproto_client.request.RequestBase.add_additional_headers_source). Each is a zero-argument callable returning a dict, invoked on every request. This is how the `Authorization` header stays current across token refreshes without anyone rewriting it.
4. **Per-request headers**, passed as `headers=` to an individual call.

```python
client.request.add_additional_header('X-Trace-Id', 'abc123')
client.request.set_additional_headers({'X-Trace-Id': 'abc123'})  # replaces the whole dict
client.request.add_additional_headers_source(lambda: {'X-Request-Time': now()})
```

:::{attention}
`set_additional_headers` replaces the dict wholesale. Calling it after `with_proxy` or `with_labelers` drops the header they set. Use `add_additional_header` to add one without disturbing the others.
:::

If you want the header without the clone, to configure a client once at construction, call [configure_proxy_header](#atproto_client.client.client.Client.configure_proxy_header) or [configure_labelers_header](#atproto_client.client.client.Client.configure_labelers_header) directly. They mutate the client they are called on and return `None`.
