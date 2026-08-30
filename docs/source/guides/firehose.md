# Firehose

The firehose is the network's event stream. A relay aggregates every commit from every PDS it crawls and republishes them over one websocket, so you see each created, deleted, liked and reposted record as it happens. A second stream carries labels from moderation services.

The wire format is described in the [event stream specification](https://atproto.com/specs/event-stream); the public relay is documented at [bsky.network/docs/relay](https://bsky.network/docs/relay).

## Subscribing to repository events

You write a callback; the client calls it for every message frame it receives. [parse_subscribe_repos_message](#atproto_firehose.parse_subscribe_repos_message) turns the frame into the model for its type.

::::{tab-set}
:::{tab-item} Sync
```{literalinclude} ../../../examples/firehose/sub_repos.py
:language: python
:caption: examples/firehose/sub_repos.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/firehose/sub_repos_async.py
:language: python
:caption: examples/firehose/sub_repos_async.py
```
:::
::::

`start` blocks until the client is stopped. The async client takes an asynchronous callback and is awaited.

[FirehoseSubscribeReposClient](#atproto_firehose.FirehoseSubscribeReposClient) defaults to `wss://bsky.network/xrpc`, the public relay. Pass `base_uri` to subscribe to a single PDS instead.

## Subscribing to label events

Labels come from a moderation service rather than a relay, so [FirehoseSubscribeLabelsClient](#atproto_firehose.FirehoseSubscribeLabelsClient) defaults to `wss://mod.bsky.app/xrpc`, the Bluesky moderation service. Everything else is the same.

```{literalinclude} ../../../examples/firehose/sub_labels.py
:language: python
:caption: examples/firehose/sub_labels.py
```

## Decoding commits

`parse_subscribe_repos_message` does not decode the inner DAG-CBOR. A `ComAtprotoSyncSubscribeRepos.Commit` carries its records as a CAR file in `blocks`, and the `ops` list tells you which CID in that file belongs to which path. Decode it with [CAR](#atproto_core.car.CAR):

```python
from atproto import CAR, models


def on_message_handler(message) -> None:
    commit = parse_subscribe_repos_message(message)
    # we need to be sure that it's a commit message with .blocks inside
    if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
        return

    if not commit.blocks:
        return

    car = CAR.from_bytes(commit.blocks)
```

`car.blocks` maps [CID](#atproto_core.cid.CID) to raw record data; `car.root` is the commit object itself. The full version, resolving each op to an [AtUri](#atproto_core.uri.AtUri) then looking the record up in the CAR and turning it into a model, is worked through in the examples below, which also fan the work out to a process pool because a single Python process cannot keep up with the relay at peak:

::::{tab-set}
:::{tab-item} Sync
```{literalinclude} ../../../examples/firehose/process_commits.py
:language: python
:caption: examples/firehose/process_commits.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/firehose/process_commits_async.py
:language: python
:caption: examples/firehose/process_commits_async.py
```
:::
::::

:::{tip}
Your callback runs on the receive loop. Anything slow in it, a database write or an HTTP call, is backpressure on the socket, and the relay disconnects consumers that fall too far behind. Hand the frame to a queue and do the work elsewhere.
:::

## Filter before you parse

Parsing is the expensive part. The frame header is already decoded when your callback is called, so discard the messages you do not want first:

```python
def on_message_handler(message: firehose_models.MessageFrame) -> None:
    if message.type != '#commit':
        return

    commit = parse_subscribe_repos_message(message)
```

`message.type` is the `t` field of [message.header](#atproto_subscription.frames.MessageFrame), one of `#commit`, `#sync`, `#identity`, `#account` or `#info` on the repos stream.

:::{note}
`parse_subscribe_repos_message` raises `KeyError` on a message type it does not know, which is what a newly added event type looks like to an older SDK. Filtering on the header first also protects you from that.
:::

## Cursors

Every commit carries a `seq`. Pass one back as the `cursor` param and the relay replays everything after it, which is how you avoid a gap across a restart.

The cursor you started with is the cursor the client reconnects with. It is not advanced for you. Call [update_params](#atproto_firehose.FirehoseSubscribeReposClient.update_params) as you process messages so that a reconnect resumes from where you actually are:

```python
def on_message_handler(message: firehose_models.MessageFrame) -> None:
    commit = parse_subscribe_repos_message(message)
    if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
        return

    if commit.seq % 20 == 0:
        client.update_params(models.ComAtprotoSyncSubscribeRepos.Params(cursor=commit.seq))
```

:::{warning}
If you pass `params` when you construct the client and never update them, a reconnect rolls the stream back to the cursor you started with and you reprocess everything since.
:::

`update_params` accepts a params model or a plain dict, and takes effect on the next connection, not the current one. Persisting the cursor every message is usually wasteful; every N messages, as above, bounds how much you replay after a crash.

## Reconnects and recv_timeout

The client reconnects on its own. Connection errors (a dropped socket, a failed handshake, an oversized frame) are not raised to you; the client backs off and dials again. The delay doubles per attempt up to 64 seconds, with a small random offset so a fleet of consumers does not return in lockstep. A connection that stayed up for at least a minute resets the backoff to its base delay rather than reconnecting instantly, for the same reason: when a relay restarts it drops every consumer at once.

`recv_timeout` is how long the client waits for a frame before deciding the connection is dead and reconnecting. It defaults to 30 seconds for the repos stream and 5 minutes for labels, which is idle time rather than total time, because the labels stream is quiet for long stretches and needs the longer window. Raise it if you subscribe to something quieter still; `None` disables the timeout, which means a silently half-open connection is never noticed.

Two things do stop the client. A server-sent error frame is raised as `SubscriptionError`, and a clean close by the server ends `start` without an exception. Frames that fail to decode are neither: one bad frame is skipped rather than killing the connection.

## Stopping the client

`stop` is safe to call from another thread or task, and takes effect even while the client is idle waiting for the next frame.

::::{tab-set}
:::{tab-item} Sync
```{literalinclude} ../../../examples/firehose/stop_client.py
:language: python
:caption: examples/firehose/stop_client.py
```
:::
:::{tab-item} Async
```{literalinclude} ../../../examples/firehose/stop_client_async.py
:language: python
:caption: examples/firehose/stop_client_async.py
```
:::
::::

## Errors in your callback

An exception raised by your callback does not stop the stream. Without a second callback the traceback is printed and the next message is processed; pass one and it is called with the exception instead.

```{literalinclude} ../../../examples/firehose/handle_errors.py
:language: python
:caption: examples/firehose/handle_errors.py
```

The error callback is called on the receive loop too, and an exception raised inside it is printed and swallowed.

## Which client to use

`FirehoseSubscribeReposClient` and `FirehoseSubscribeLabelsClient` are thin subclasses of the generated subscription clients that fill in the deployment details: the relay and moderation service hostnames, and the `recv_timeout` appropriate to each stream. The generated clients underneath take `base_uri` as their first, required argument and default `recv_timeout` to `None`:

| Client                                       | Subscription                              | Parser                                                    |
| -------------------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| `ComAtprotoSyncSubscribeReposClient`         | `com.atproto.sync.subscribeRepos`         | `parse_com_atproto_sync_subscribe_repos_message`          |
| `ComAtprotoLabelSubscribeLabelsClient`       | `com.atproto.label.subscribeLabels`       | `parse_com_atproto_label_subscribe_labels_message`        |
| `ChatBskyModerationSubscribeModEventsClient` | `chat.bsky.moderation.subscribeModEvents` | `parse_chat_bsky_moderation_subscribe_mod_events_message` |

Each has an `Async` counterpart with the same name and arguments. They live in `atproto_client.subscriptions` and are generated from the lexicons, so a subscription added to the protocol gets a client without anything being written by hand.

`ChatBskyModerationSubscribeModEventsClient` has no `Firehose*` alias because it has no public host: it is the moderation event stream of a chat service, and you point it at your own.

```python
from atproto_client.subscriptions import (
    ChatBskyModerationSubscribeModEventsClient,
    parse_chat_bsky_moderation_subscribe_mod_events_message,
)

client = ChatBskyModerationSubscribeModEventsClient('wss://my-chat-service.example.com/xrpc')


def on_message_handler(message) -> None:
    print(parse_chat_bsky_moderation_subscribe_mod_events_message(message))


client.start(on_message_handler)
```

All of them are [SubscriptionClient](#atproto_subscription.client.SubscriptionClient)s, which is where `start`, `stop`, `update_params` and the reconnect behaviour described above actually live.

## Firehose or Jetstream?

[Jetstream](jetstream.md) carries the same events as JSON, filtered server-side, with no CAR or DAG-CBOR decoding to do. It is dramatically cheaper to consume, and it is the right default for most consumers.

The firehose is what you want when you need what Jetstream drops. Jetstream events carry no repository signatures and no MST proofs, so they cannot be cryptographically verified; firehose commits can. The firehose also gives you the raw blocks, which is what you need if you are mirroring repositories rather than reacting to records.

More code examples: <https://github.com/MarshalX/atproto/tree/main/examples/firehose>
