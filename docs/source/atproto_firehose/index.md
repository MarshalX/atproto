# Firehose (data streaming)

The firehose clients and the deployment values they carry: today's relay host, the reconnect timeout, and the per-lexicon message parsers. The subscription machinery underneath them lives in [atproto_subscription](../atproto_subscription/index.md).

Four clients, sync and async, over two lexicons:

[FirehoseSubscribeReposClient](#atproto_firehose.FirehoseSubscribeReposClient) / [AsyncFirehoseSubscribeReposClient](#atproto_firehose.AsyncFirehoseSubscribeReposClient)
: `com.atproto.sync.subscribeRepos`, every repository commit on the network.

[FirehoseSubscribeLabelsClient](#atproto_firehose.FirehoseSubscribeLabelsClient) / [AsyncFirehoseSubscribeLabelsClient](#atproto_firehose.AsyncFirehoseSubscribeLabelsClient)
: `com.atproto.label.subscribeLabels`, labels published by a moderation service.

:::{tip}
For how to use these, covering decoding commits, filtering, cursors, reconnects and choosing between the firehose and Jetstream, see the [Firehose guide](../guides/firehose.md).
:::

:::{note}
`atproto_firehose.client` and `atproto_firehose.models` are deprecation shims. The subscription runtime moved to `atproto_subscription.client` and the frame models to `atproto_subscription.frames`; `atproto.firehose_models` points at the latter and is not deprecated.
:::

```{eval-rst}
.. automodule:: atproto_firehose
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

models
```
