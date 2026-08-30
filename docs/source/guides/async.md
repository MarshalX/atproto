# Async

Every part of the SDK that does I/O comes in two forms. The async one is the same API with `Async` in front of the name and `await` in front of the call.

| Sync                            | Async                                |
| ------------------------------- | ------------------------------------ |
| `Client`                        | `AsyncClient`                        |
| `Request`                       | `AsyncRequest`                       |
| `IdResolver`                    | `AsyncIdResolver`                    |
| `DidInMemoryCache`              | `AsyncDidInMemoryCache`              |
| `FirehoseSubscribeReposClient`  | `AsyncFirehoseSubscribeReposClient`  |
| `FirehoseSubscribeLabelsClient` | `AsyncFirehoseSubscribeLabelsClient` |
| `JetstreamClient`               | `AsyncJetstreamClient`               |

```python
import asyncio

from atproto import AsyncClient


async def main() -> None:
    client = AsyncClient()
    await client.login('my-handle.bsky.social', 'my-password')
    await client.send_post(text='Hello from asyncio')


asyncio.run(main())
```

## The method sets are identical

`AsyncClient` and the async namespaces are not written by hand. They are generated from the sync ones by the SDK's own codegen. A method exists on one exactly when it exists on the other, with the same name, the same arguments and the same return type.

So anything in these guides written against `Client` applies unchanged to `AsyncClient`: put an `await` in front of it. Where the two genuinely differ, the guides show both in a tab set.

## Running calls concurrently

This is the reason to use the async client at all. Independent requests should be in flight together, not one after another:

```python
import asyncio

from atproto import AsyncClient


async def main() -> None:
    client = AsyncClient()
    await client.login('my-handle.bsky.social', 'my-password')

    handles = ['bsky.app', 'atproto.com', 'marshal.dev']
    profiles = await asyncio.gather(*[client.get_profile(handle) for handle in handles])

    for profile in profiles:
        print(profile.handle, profile.followers_count)


asyncio.run(main())
```

One `AsyncClient` is safe to use from many coroutines at once. Token refresh is guarded by an `asyncio.Lock`, so concurrent calls that all find an expiring token refresh once rather than racing.

:::{warning}
Concurrency is exactly how you hit rate limits. `asyncio.gather` over a thousand handles sends a thousand requests as fast as the connection pool allows. Batch, or bound the fan-out with a `Semaphore`. See [Error handling](error-handling.md#rate-limits).
:::

## Session callbacks

[on_session_change](#atproto_client.client.client.Client.on_session_change) on the async client accepts **both** synchronous and asynchronous callbacks. Coroutine functions are awaited; plain functions are called directly. Register either, or one of each:

```python
@client.on_session_change
async def persist(event: SessionEvent, session: Session) -> None:
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        await save_session(session.export())
```

The sync client only calls synchronous callbacks. An `async def` registered on it is stored and never invoked. See [Authentication](authentication.md).

## Streaming clients and the event loop

The firehose and jetstream clients are the one place where the choice is not cosmetic.

`start()` on a **sync** streaming client blocks the calling thread in a receive loop until `stop()` is called or the connection ends for good. Calling it from inside a coroutine freezes the event loop and everything else on it. Use the async client there, or run the sync one in a separate thread.

`start()` on an **async** streaming client is a coroutine that drives your callback on the loop. Your `on_message_callback` must be `async def`, and it must not block: while it runs, no further frames are read. The firehose moves faster than most per-message work, so hand anything slow to a queue or an executor and return.

```python
import asyncio

from atproto import AsyncFirehoseSubscribeReposClient, parse_subscribe_repos_message


async def on_message(message) -> None:
    commit = parse_subscribe_repos_message(message)
    await queue.put(commit)  # do the real work elsewhere


async def main() -> None:
    client = AsyncFirehoseSubscribeReposClient()
    await client.start(on_message)


asyncio.run(main())
```

`stop()` is safe to call from another task on the async client, and from another thread on the sync one, including while the client is idle, waiting on the next frame.
