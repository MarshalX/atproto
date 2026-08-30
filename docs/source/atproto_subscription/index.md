# Subscription

The runtime behind every AT Protocol subscription: a reconnecting websocket client, the XRPC frame format, and the callback loop that hands decoded frames to your code. It is lexicon-agnostic: it knows how a subscription behaves, not what any particular one carries.

Three things sit on top of it. [Firehose](../guides/firehose.md) and [Jetstream](../guides/jetstream.md) are the two you use directly, and every generated subscription client in `atproto_client.subscriptions`, including the ones with no hand-written wrapper such as `ChatBskyModerationSubscribeModEventsClient`, is a `SubscriptionClient` with a method name and a parser bound to it.

You reach for this package directly when you are subscribing to a lexicon the SDK has no convenience client for, and when you want the semantics: what `recv_timeout` does, when the client reconnects, and how `update_params` survives one. Those are covered in [Firehose](../guides/firehose.md), and they apply to every subscription.

```python
from atproto_subscription import SubscriptionClient

client = SubscriptionClient(
    method='com.example.subscribeThings',
    base_uri='wss://example.com/xrpc',
    params={'cursor': 42},
)


def on_message_handler(message) -> None:
    print(message.header, message.body)


client.start(on_message_handler)
```

`start` blocks until [stop](#atproto_subscription.websocket.WebsocketClient.stop) is called, the server closes cleanly, or the server sends an error frame. `AsyncSubscriptionClient` is the same client with awaited callbacks.

:::{note}
This package was factored out of `atproto_firehose`, which is why the frame models are re-exported as `atproto.firehose_models`. `atproto_firehose.client` and `atproto_firehose.models` are deprecation shims that forward here and warn: `FirehoseClient` and `AsyncFirehoseClient` are now [SubscriptionClient](#atproto_subscription.client.SubscriptionClient) and [AsyncSubscriptionClient](#atproto_subscription.client.AsyncSubscriptionClient), and the frame models moved to [atproto_subscription.frames](frames.md). The `FirehoseSubscribeReposClient` and `FirehoseSubscribeLabelsClient` you actually use are unaffected.
:::

```{eval-rst}
.. automodule:: atproto_subscription
   :members:
   :undoc-members:
   :inherited-members:
```

## Submodules

```{toctree}
:maxdepth: 4

client
frames
websocket
```
