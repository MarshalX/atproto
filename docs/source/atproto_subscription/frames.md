# Frame models

The wire format of AT Protocol XRPC subscriptions: each frame is two concatenated DAG-CBOR items, a header and a body. [Frame.from_bytes](#atproto_subscription.frames.Frame.from_bytes) decodes one into a [MessageFrame](#atproto_subscription.frames.MessageFrame) or an [ErrorFrame](#atproto_subscription.frames.ErrorFrame), depending on the `op` field of its [header](#atproto_subscription.frames.FrameHeader).

A message frame carries `header.t`, its type such as `#commit`, and an undecoded `body`. That type is what the per-lexicon parsers (`parse_subscribe_repos_message` and friends) dispatch on, and what you filter on to avoid parsing messages you do not want.

:::{note}
These are re-exported as `atproto.firehose_models`, which is the import you will see in the examples and in most existing code.
:::

```{eval-rst}
.. automodule:: atproto_subscription.frames
   :members:
   :undoc-members:
   :show-inheritance:
```
