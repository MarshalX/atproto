import asyncio
import queue
import threading
import typing as t

from atproto_subscription.websocket import AsyncWebsocketClient, WebsocketClient

from atproto_jetstream.models import SubscribeEventsMessage

#: Bounds memory if the consumer is slower than the tail.
_QUEUE_SIZE = 1024


def iter_live(client: WebsocketClient[SubscribeEventsMessage]) -> t.Iterator[SubscribeEventsMessage]:
    """Drive a running live client from a background thread and yield its events.

    `start()` is a blocking callback loop, but `replay()` is an iterator.
    """
    # None marks the end of the stream
    events: queue.Queue[t.Optional[SubscribeEventsMessage]] = queue.Queue(maxsize=_QUEUE_SIZE)
    failure: t.List[BaseException] = []

    def on_message(message: SubscribeEventsMessage) -> None:
        events.put(message)

    def run() -> None:
        try:
            client.start(on_message)
        except BaseException as e:  # noqa: BLE001
            failure.append(e)
        finally:
            events.put(None)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    try:
        while True:
            item = events.get()
            if item is None:
                break

            yield item
    finally:
        client.stop()

    if failure:
        raise failure[0]


async def iter_live_async(
    client: AsyncWebsocketClient[SubscribeEventsMessage],
) -> t.AsyncIterator[SubscribeEventsMessage]:
    """Async twin of :obj:`iter_live`."""
    events: asyncio.Queue[t.Optional[SubscribeEventsMessage]] = asyncio.Queue(maxsize=_QUEUE_SIZE)
    failure: t.List[BaseException] = []

    async def on_message(message: SubscribeEventsMessage) -> None:
        await events.put(message)

    async def run() -> None:
        try:
            await client.start(on_message)
        except BaseException as e:  # noqa: BLE001
            failure.append(e)
        finally:
            await events.put(None)

    task = asyncio.ensure_future(run())

    try:
        while True:
            item = await events.get()
            if item is None:
                break

            yield item
    finally:
        await client.stop()
        if not task.done():
            task.cancel()

    if failure:
        raise failure[0]
