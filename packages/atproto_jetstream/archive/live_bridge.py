import asyncio
import queue
import threading
import typing as t

from atproto_jetstream.models import SubscribeEventsMessage

#: Bounds memory if the consumer is slower than the tail.
_QUEUE_SIZE = 1024

_SENTINEL = object()


def iter_live(client: t.Any) -> t.Iterator[SubscribeEventsMessage]:
    """Drive a running live client from a background thread and yield its events.

    `start()` is a blocking callback loop, but `replay()` is an iterator.
    """
    events: queue.Queue[t.Any] = queue.Queue(maxsize=_QUEUE_SIZE)
    failure: t.List[BaseException] = []

    def on_message(message: SubscribeEventsMessage) -> None:
        events.put(message)

    def run() -> None:
        try:
            client.start(on_message)
        except BaseException as e:  # noqa: BLE001
            failure.append(e)
        finally:
            events.put(_SENTINEL)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    try:
        while True:
            item = events.get()
            if item is _SENTINEL:
                break

            yield item
    finally:
        client.stop()

    if failure:
        raise failure[0]


async def iter_live_async(client: t.Any) -> t.AsyncIterator[SubscribeEventsMessage]:
    """Async twin of :obj:`iter_live`."""
    events: asyncio.Queue[t.Any] = asyncio.Queue(maxsize=_QUEUE_SIZE)
    failure: t.List[BaseException] = []

    async def on_message(message: SubscribeEventsMessage) -> None:
        await events.put(message)

    async def run() -> None:
        try:
            await client.start(on_message)
        except BaseException as e:  # noqa: BLE001
            failure.append(e)
        finally:
            await events.put(_SENTINEL)

    task = asyncio.ensure_future(run())

    try:
        while True:
            item = await events.get()
            if item is _SENTINEL:
                break

            yield item
    finally:
        await client.stop()
        if not task.done():
            task.cancel()

    if failure:
        raise failure[0]
