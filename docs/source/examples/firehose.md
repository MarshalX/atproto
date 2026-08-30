# Firehose

The firehose is the whole network's event stream, delivered as signed, verifiable [CAR](#atproto_core.car.car.CAR) blocks over a websocket. For the prose, see [Firehose](../guides/firehose.md); if you do not need cryptographic verifiability, [Jetstream](jetstream.md) is cheaper to consume.

## Subscribe to repository events

The minimum: connect, and print every frame.

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

## Subscribe to label events

A separate stream, carrying moderation labels rather than repository commits.

```{literalinclude} ../../../examples/firehose/sub_labels.py
:language: python
:caption: examples/firehose/sub_labels.py
```

## Decode commits into records

A commit frame carries a CAR file of blocks. Getting the records out means decoding it and looking up each operation's CID.

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

## Stop the client

`stop()` closes the connection after the current message.

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

## Handle errors

A long-lived stream will disconnect. Catch the error and reconnect from your stored cursor.

```{literalinclude} ../../../examples/firehose/handle_errors.py
:language: python
:caption: examples/firehose/handle_errors.py
```
