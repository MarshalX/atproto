# Jetstream

Jetstream delivers the same events as the firehose as plain JSON, filtered server-side, with no CAR or DAG-CBOR decoding. For the prose on filtering, cursors, compression and the metered archive, see [Jetstream](../guides/jetstream.md).

## Subscribe to everything

```{literalinclude} ../../../examples/jetstream/sub_events.py
:language: python
:caption: examples/jetstream/sub_events.py
```

## Filter for posts

Filters are applied by the server, so you only pay for what you asked for.

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

## Resume from a stored cursor

The client tracks the cursor across reconnects on its own. Persist it to survive a restart too.

```{literalinclude} ../../../examples/jetstream/resume_from_cursor.py
:language: python
:caption: examples/jetstream/resume_from_cursor.py
```

## Replay the archive

`snapshot()` sweeps the sealed archive and stops. `replay()` sweeps it and continues into the live tail without a gap, so a consumer cannot tell where one ended and the other began.

:::{warning}
The archive is metered in **bytes downloaded**, not requests, and the whole network is roughly 1.85 TB. Filter selectively and check `bytes_downloaded`. See [Metering](../guides/jetstream.md#metering).
:::

::::{tab-set}
:::{tab-item} Archive only
```{literalinclude} ../../../examples/jetstream/backfill_snapshot.py
:language: python
:caption: examples/jetstream/backfill_snapshot.py
```
:::
:::{tab-item} Archive, then live
```{literalinclude} ../../../examples/jetstream/backfill_then_live.py
:language: python
:caption: examples/jetstream/backfill_then_live.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/jetstream/backfill_async.py
:language: python
:caption: examples/jetstream/backfill_async.py
```
:::
::::
