# Subscription client

[SubscriptionClient](#atproto_subscription.client.SubscriptionClient) and [AsyncSubscriptionClient](#atproto_subscription.client.AsyncSubscriptionClient) add XRPC frame decoding to the reconnecting [websocket client](websocket.md), which is where [start](#atproto_subscription.websocket.WebsocketClient.start), [stop](#atproto_subscription.websocket.WebsocketClient.stop) and [update_params](#atproto_subscription.websocket.WebsocketClientBase.update_params) are documented.

`start` runs the receive loop and calls your callback per message frame; `stop` ends it from another thread or task, even while the connection is idle; `update_params` replaces the query params used for the *next* connection, which is how a cursor survives a reconnect. This layer overrides it to accept a params model as well as a dict.

A frame that cannot be decoded is skipped rather than killing the connection; an error frame from the server raises `SubscriptionError`. `recv_timeout` is idle time, not total time: the client reconnects if no frame arrives within it. Messages larger than 5 MB are rejected by the websocket layer.

```{eval-rst}
.. automodule:: atproto_subscription.client
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:
```
