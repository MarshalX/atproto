# Jetstream (data streaming)

[Jetstream](https://github.com/bluesky-social/jetstream) delivers the same events as the firehose as plain JSON, filtered server-side, with no CAR or DAG-CBOR decoding. This package holds the client, its models, and the archive replay.

[JetstreamClient](#atproto_jetstream.JetstreamClient) / [AsyncJetstreamClient](#atproto_jetstream.AsyncJetstreamClient)
: The live tail, plus `snapshot()` and `replay()` over the archive.

:::{tip}
For how to use these, covering filters, cursors, compression, archive replay and what the archive costs, see the [Jetstream guide](../guides/jetstream.md).
:::

:::{note}
Only the Jetstream v2 wire is supported. The legacy v1 hosts (`jetstream1.*`, `jetstream2.*`) speak a different, frozen protocol and will not work with this client.
:::

:::{warning}
Jetstream carries no repository signatures or MST proofs, so its data cannot be cryptographically verified. Use [FirehoseSubscribeReposClient](#atproto_firehose.FirehoseSubscribeReposClient) when verifiability matters.
:::

```{eval-rst}
.. automodule:: atproto_jetstream
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

models
archive
```
