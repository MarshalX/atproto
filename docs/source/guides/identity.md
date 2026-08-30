# Resolving identities

The AT Protocol has two identifiers. A handle is a DNS name that can change; a DID is a stable identifier that cannot. Records, sessions and tokens all use DIDs, so most of what you do with identity is turning a handle into a DID, and a DID into the document that says where the account lives and which key it signs with.

The identity rules themselves are the protocol's, not this SDK's. See [atproto.com/specs/handle](https://atproto.com/specs/handle) and [atproto.com/specs/did](https://atproto.com/specs/did).

## IdResolver

[IdResolver](#atproto_identity.resolver.IdResolver) bundles the two resolvers and shares one timeout, one PLC directory URL and one cache between them. [handle](#atproto_identity.resolver.IdResolver.handle) resolves handles to DIDs; [did](#atproto_identity.resolver.IdResolver.did) resolves DIDs to documents.

::::{tab-set}
:::{tab-item} Sync
```python
from atproto import IdResolver

resolver = IdResolver()

did = resolver.handle.resolve('test.marshal.dev')
did_doc = resolver.did.resolve(did)

print(did)
print(did_doc.get_pds_endpoint())
```
:::
:::{tab-item} Async
```python
from atproto import AsyncIdResolver

resolver = AsyncIdResolver()

did = await resolver.handle.resolve('test.marshal.dev')
did_doc = await resolver.did.resolve(did)

print(did)
print(did_doc.get_pds_endpoint())
```
:::
::::

The PLC directory defaults to `https://plc.directory` and requests time out after 3 seconds. Both are constructor arguments, along with `cache`:

```python
resolver = IdResolver(plc_url='https://plc.example.com', timeout=10.0, cache=cache)
```

Everything below is reachable through the two properties. You can also construct [HandleResolver](#atproto_identity.handle.resolver.HandleResolver) and [DidResolver](#atproto_identity.did.resolver.DidResolver) directly if you only need one of them.

## Resolving handles

[resolve](#atproto_identity.handle.resolver.HandleResolver.resolve) tries DNS first, then HTTP, and returns the first DID it gets. It returns `None` when neither method produces one: a handle that does not exist, a domain that does not answer, and a network failure are all the same `None`.

[ensure_resolve](#atproto_identity.handle.resolver.HandleResolver.ensure_resolve) is the same lookup but raises `DidNotFoundError` instead of returning `None`. Use it when a missing handle is an error you want to propagate rather than a case you want to branch on.

```python
did = resolver.handle.resolve('unknown.example.com')  # None
did = resolver.handle.ensure_resolve('unknown.example.com')  # raises DidNotFoundError
```

The two methods behind them are public, so you can pick one when you know which the account uses:

[resolve_dns](#atproto_identity.handle.resolver.HandleResolver.resolve_dns)
: Queries the `TXT` records of `_atproto.<handle>` and returns the value of the first one starting with `did=`.

[resolve_http](#atproto_identity.handle.resolver.HandleResolver.resolve_http)
: Fetches `https://<handle>/.well-known/atproto-did` and returns the first line, if it starts with `did:`.

Both swallow their own failures and return `None`, so a DNS timeout falls through to the HTTP attempt rather than raising.

:::{note}
`HandleResolver` accepts a `backup_nameservers` argument, but it is not wired up yet: DNS resolution always uses the system resolver.
:::

:::{warning}
A handle resolved this way is not proof of ownership. The DID document is authoritative. An account is only really `alice.example.com` if the document its DID resolves to lists that handle in `alsoKnownAs`. Resolve the DID back and compare when it matters.
:::

## Resolving DIDs

[resolve](#atproto_identity.did.resolver.DidResolver.resolve) returns a [DidDocument](#atproto_core.did_doc.DidDocument), or `None` if the DID does not exist. It validates what it fetched: the document must parse, and its `id` must equal the DID you asked for, or `PoorlyFormattedDidDocumentError` is raised. As with handles, [ensure_resolve](#atproto_identity.did.resolver.DidResolver.ensure_resolve) raises `DidNotFoundError` rather than returning `None`.

[resolve_without_validation](#atproto_identity.did.resolver.DidResolver.resolve_without_validation) returns the raw JSON as a `dict` and skips every check above, including the cache. Reach for it when you want to see what a directory actually served, such as debugging a document the validator rejects.

`force_refresh=True` bypasses the cache for a single call and rewrites the entry with what it fetched:

```python
did_doc = resolver.did.resolve(did, force_refresh=True)
```

### PLC and did:web

The method segment of the DID picks the resolver:

`did:plc:...`
: Fetched from the PLC directory as `<plc_url>/<did>`. A `404` means the DID does not exist and resolves to `None`; any other HTTP failure raises `DidPlcResolverError`.

`did:web:...`
: Fetched from `https://<host>/.well-known/did.json`, where the host is the rest of the DID. Failures raise `DidWebResolverError`.

Anything else raises `UnsupportedDidMethodError`, and a string that is not a DID at all raises `PoorlyFormattedDidError`.

:::{attention}
`did:web` paths are not supported. `did:web:example.com` resolves; `did:web:example.com:user:alice` raises `UnsupportedDidWebPathError`. Only host-level documents are accepted, which is what the AT Protocol allows.
:::

### Pulling atproto data out of a document

A DID document is a generic W3C structure. The three fields that matter for the AT Protocol (signing key, handle and PDS) are extracted by [AtprotoData](#atproto_identity.did.atproto_data.AtprotoData):

```python
from atproto_identity.did.atproto_data import AtprotoData

data = AtprotoData.from_did_doc(did_doc)
print(data.did, data.handle, data.pds, data.signing_key)
```

Any of `signing_key`, `handle` and `pds` can be `None` when the document does not carry it. [ensure_atproto_document](#atproto_identity.did.atproto_data.ensure_atproto_document) does the same extraction and raises `AtprotoDataParseError` if any of the three is missing, so what it returns is fully populated. [ensure_atproto_key](#atproto_identity.did.atproto_data.ensure_atproto_key) checks only the signing key and returns it as a `did:key` string.

The resolver has both as one-step methods, which resolve the DID and extract in a single call:

```python
data = resolver.did.resolve_atproto_data(did)  # AtprotoData, fully populated
key = resolver.did.resolve_atproto_key(did)  # 'did:key:zQ3s...'
```

`resolve_atproto_key` returns its argument unchanged if you hand it something that is already a `did:key`, so it is safe to call on an issuer that may be either.

This is the call a service makes to verify an inbound request: the signing key of the DID that issued a service-auth JWT is what you check the signature against. See [Building a feed generator](feed-generator.md).

## Caching

Every resolution is an HTTP request. A DID document changes rarely, so a service that resolves the same DIDs repeatedly, on every feed request and every verified token, should cache them.

Pass a cache to the resolver and it is used automatically:

```python
from atproto import DidInMemoryCache, IdResolver

cache = DidInMemoryCache()
resolver = IdResolver(cache=cache)

did_doc = resolver.did.resolve('did:web:feed.atproto.blue')  # network
did_doc = resolver.did.resolve('did:web:feed.atproto.blue')  # cache

cache.clear()

did_doc = resolver.did.resolve('did:web:feed.atproto.blue')  # network again
```

Use `AsyncDidInMemoryCache` with `AsyncIdResolver`; the two must match, since one awaits its cache and the other does not.

### stale_ttl and max_ttl

A cache entry has two ages, both constructor arguments on every cache:

`stale_ttl`
: Default 1 hour. Past it the entry is still served, and a refresh is kicked off first, so the caller gets a document without waiting for the network, and the next caller gets the fresh one.

`max_ttl`
: Default 1 day. Past it the entry is not served at all; the resolver fetches, and stores what it fetched.

```python
cache = DidInMemoryCache(stale_ttl=60 * 5, max_ttl=60 * 60)
```

A resolution that returns nothing deletes the entry, so an account that disappears does not stay cached until `max_ttl`.

### Writing your own cache

[DidInMemoryCache](#atproto_identity.cache.in_memory_cache.DidInMemoryCache) is a dict and dies with the process. For anything with more than one worker, subclass [DidBaseCache](#atproto_identity.cache.base_cache.DidBaseCache), or [AsyncDidBaseCache](#atproto_identity.cache.base_cache.AsyncDidBaseCache), and implement the five methods. Here is the shape of a Redis-backed one:

```python
import json
import typing as t
from datetime import datetime, timezone

from atproto_core.did_doc import DidDocument
from atproto_identity.cache.base_cache import DidBaseCache, GetDocCallback
from atproto_identity.cache.models import CachedDidResult


class DidRedisCache(DidBaseCache):
    def __init__(self, redis, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)
        self._redis = redis

    def get(self, did: str) -> t.Optional[CachedDidResult]:
        raw = self._redis.hgetall(did)
        if not raw:
            return None

        updated_at = datetime.fromisoformat(raw['updated_at'])
        age = (datetime.now(timezone.utc) - updated_at).total_seconds()

        return CachedDidResult(
            did=did,
            document=DidDocument.from_dict(json.loads(raw['document'])),
            updated_at=updated_at,
            stale=age > self.stale_ttl,
            expired=age > self.max_ttl,
        )

    def set(self, did: str, document: DidDocument) -> None:
        self._redis.hset(
            did,
            mapping={
                'document': document.model_dump_json(by_alias=True),
                'updated_at': datetime.now(timezone.utc).isoformat(),
            },
        )
        self._redis.expire(did, self.max_ttl)

    def refresh(self, did: str, get_doc_callback: GetDocCallback) -> None:
        document = get_doc_callback()
        if document:
            self.set(did, document)

    def delete(self, did: str) -> None:
        self._redis.delete(did)

    def clear(self) -> None:
        raise NotImplementedError
```

Three things the resolver relies on:

- `get` decides `stale` and `expired` itself, by comparing `updated_at` against `stale_ttl` and `max_ttl`. The resolver only reads the flags. Returning `None` means "not cached".
- `refresh` is called when an entry has gone stale but not expired. The callback it is handed performs the network resolution and may return `None`; store only a document. This is the hook a shared cache uses to make sure one worker refreshes rather than all of them. Take a lock around the callback.
- `delete` is called for a DID that failed to resolve, whether or not it was cached, so it must tolerate a key that is not there.

## Exceptions

Everything below is raised from `atproto_identity.exceptions` and inherits from `AtProtocolError`, so one `except AtProtocolError` catches the lot.

| Exception                         | Raised when                                           |
| --------------------------------- | ----------------------------------------------------- |
| `DidNotFoundError`                | `ensure_resolve` found nothing, for a handle or a DID |
| `PoorlyFormattedDidError`         | the string is not a well-formed DID                   |
| `UnsupportedDidMethodError`       | the DID method is neither `plc` nor `web`             |
| `UnsupportedDidWebPathError`      | a `did:web` carries a path                            |
| `PoorlyFormattedDidDocumentError` | the document did not parse, or its `id` did not match |
| `DidPlcResolverError`             | the PLC directory request failed                      |
| `DidWebResolverError`             | the `did:web` request failed                          |
| `AtprotoDataParseError`           | the document is missing a signing key, handle or PDS  |
