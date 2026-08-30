# Jetstream

[Jetstream](https://github.com/bluesky-social/jetstream) is a streaming service for the AT Protocol network. Unlike the [firehose](firehose.md), it delivers records as plain JSON, filters server-side, and needs no CAR or DAG-CBOR decoding. The public service is documented at [bsky.network/docs/jetstream](https://bsky.network/docs/jetstream).

:::{note}
Only the Jetstream v2 wire is supported. The legacy v1 hosts (`jetstream1.*`, `jetstream2.*`) speak a different, frozen protocol and will not work with this client.
:::

:::{note}
Jetstream carries no repository signatures or MST proofs, so its data cannot be cryptographically verified. Use [FirehoseSubscribeReposClient](#atproto_firehose.FirehoseSubscribeReposClient) when verifiability matters.
:::

## Subscribing

Both clients are present in two variants: sync and async. You write a callback; the client calls it for every event.

```{literalinclude} ../../../examples/jetstream/sub_events.py
:language: python
:caption: examples/jetstream/sub_events.py
```

The record arrives as JSON, so no CAR or DAG-CBOR decoding is needed. A commit's `record` is already a model; a record that does not conform to its lexicon falls back to `DotDict`.

## Filtering

Filters are applied by the server, so you receive only what you asked for:

::::{tab-set}
:::{tab-item} Sync
```{literalinclude} ../../../examples/jetstream/process_posts.py
:language: python
:caption: examples/jetstream/process_posts.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/jetstream/process_posts_async.py
:language: python
:caption: examples/jetstream/process_posts_async.py
```
:::
::::

The three filters are independent and combined with AND. Each matches everything when omitted:

- `kinds`: `commit`, `identity`, `account`, `sync`.
- `dids`: repositories to receive events for. Applies to every kind.
- `collections`: NSIDs or `<prefix>.*` patterns.

:::{warning}
`collections` constrains **commit events only**. Identity, account, and sync events are delivered regardless of it, because they are the only signals telling you an account was deactivated or deleted. Pass `kinds=['commit']` to get a commits-only stream.
:::

## Cursor and reconnects

The cursor is tracked for you. Reconnects resume from the last delivered event, and events the server replays are dropped before reaching your callback, so you never see a gap or a duplicate.

Persist [cursor](#atproto_jetstream.JetstreamClient.cursor) to resume across restarts:

```{literalinclude} ../../../examples/jetstream/resume_from_cursor.py
:language: python
:caption: examples/jetstream/resume_from_cursor.py
```

:::{note}
Cursors are instance-local and are not portable between servers or between Jetstream versions.
:::

## Compression

Frames are compressed by default using Jetstream's dict-zstd scheme, which cuts bandwidth by roughly 60%. The client fetches the server's dictionary over HTTPS once at startup, negotiates it on the websocket, and decompresses each frame transparently. Your callback sees the same models either way.

```python
client = JetstreamClient()
print(client.compressed)  # False until the first connection negotiates it
```

Compression is best-effort and never fatal. If the dictionary cannot be fetched, or the server rotates it and the new one cannot be obtained, the client falls back to an uncompressed stream and keeps running. Check [compressed](#atproto_jetstream.JetstreamClient.compressed) to see what the current connection negotiated.

Pass `compress=False` to disable it:

```python
client = JetstreamClient(compress=False)
```

:::{note}
Decompression costs roughly 2 microseconds per frame, about 12% of the time spent turning a frame into a model.
:::

## Archive replay

Jetstream keeps the whole network's history and can replay it. Pass an `api_key` and use [snapshot](#atproto_jetstream.JetstreamClient.snapshot) for the sealed archive:

::::{tab-set}
:::{tab-item} Sync
```{literalinclude} ../../../examples/jetstream/backfill_snapshot.py
:language: python
:caption: examples/jetstream/backfill_snapshot.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/jetstream/backfill_async.py
:language: python
:caption: examples/jetstream/backfill_async.py
```
:::
::::

Or [replay](#atproto_jetstream.JetstreamClient.replay) to sweep the archive and continue into the live tail without a gap:

```{literalinclude} ../../../examples/jetstream/backfill_then_live.py
:language: python
:caption: examples/jetstream/backfill_then_live.py
```

Both yield the same models the live tail delivers, so a consumer cannot tell whether an event came from a segment or the socket. The async client mirrors this with `async for`.

Record CIDs are not stored in the archive; the client derives each one from the record's CBOR, matching what the PDS reports.

:::{note}
Get a key at [bsky.network/account](https://bsky.network/account). It is **not** an AT Protocol credential: a PDS session token and a `com.atproto.server.getServiceAuth` token are both rejected. The key is used only for the archive, never on the websocket, and a self-hosted Jetstream needs none.
:::

## Metering

:::{warning}
The archive is **metered in bytes downloaded**, not requests. The whole network is roughly 1.85 TB. Check [bytes_downloaded](#atproto_jetstream.JetstreamClient.bytes_downloaded) to see what a sweep cost.
:::

What a filter costs depends on how *selective* it is, not on whether one is set. Every filter is sent to the planner, but segments carry per-DID bloom filters, so `dids` prunes hard while a popular collection appears in nearly every block and prunes almost nothing. Planning the whole archive:

| filter                               | segments matched | blocks    |
| ------------------------------------ | ---------------- | --------- |
| `dids=['did:plc:...']`               | 1 of 7,075       | 1         |
| `collections=['app.bsky.feed.post']` | 7,075 of 7,075   | 5,363,406 |

To follow a busy collection, resume from a stored cursor rather than sweeping from `after_seq=0`.

The client honours the plan's download mode, so a sparse filter fetches individual blocks rather than whole 261 MB segments, and whole segments are read in HTTP `Range` slices so they never land in memory at once. If the quota is exhausted the server replies `429` with `Retry-After`, and the client waits it out rather than retrying blindly.

More code examples: <https://github.com/MarshalX/atproto/tree/main/examples/jetstream>
