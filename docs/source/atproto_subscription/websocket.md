# Websocket client

The connection layer under every subscription client, and under Jetstream. It owns the lifecycle (dial, receive loop, callback dispatch, reconnect) and leaves frame decoding to its subclasses, which implement `_decode_frame` and `_handle_frame_decoding_error`.

Reconnection is automatic and exponential: the delay doubles per attempt up to 64 seconds, with a random offset of up to half a second so that a fleet of consumers does not reconnect in lockstep. A connection that stayed up for at least a minute resets the backoff to its base delay instead of retrying instantly, because a server restart drops every consumer at once. A clean close by the server ends the loop; a transport failure does not.

Exceptions raised by your callback never reach the loop: they go to the error callback if you passed one, and are printed otherwise.

```{eval-rst}
.. automodule:: atproto_subscription.websocket
   :members:
   :undoc-members:
   :show-inheritance:
```
