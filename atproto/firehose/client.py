from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional

import httpx
from httpx_ws import aconnect_ws, connect_ws

from atproto.exceptions import FirehoseError
from atproto.firehose.models import Frame
from atproto.xrpc_client.models.common import XrpcError

if TYPE_CHECKING:
    from atproto.firehose.models import MessageFrame

_BASE_WEBSOCKET_URL = 'https://bsky.social/xrpc'


def _build_websocket_url(method: str, base_url: Optional[str] = None) -> str:
    if base_url is None:
        base_url = _BASE_WEBSOCKET_URL

    return f'{base_url}/{method}'


class _WebsocketClientBase:
    ...


class _WebsocketClient(_WebsocketClientBase):
    def __init__(self, method: str, base_url: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        self._http_client = httpx.Client()

        url = _build_websocket_url(method, base_url)
        self._client = connect_ws(url, self._http_client, params=params)

    def start(self, on_message: Callable[['MessageFrame'], None]):
        with self._client as client:
            while True:
                raw_frame = client.receive_bytes()

                frame = Frame.from_bytes(raw_frame)
                if frame.is_error:
                    raise FirehoseError(XrpcError(frame.body.error, frame.body.message))
                elif frame.is_message:
                    on_message(frame)
                else:
                    raise FirehoseError('Unknown frame type')


class _AsyncWebsocketClient(_WebsocketClientBase):
    def __init__(self, method: str, base_url: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        self._http_client = httpx.AsyncClient()

        url = _build_websocket_url(method, base_url)
        self._client = aconnect_ws(url, self._http_client, params=params)

        self._loop = asyncio.get_event_loop()

    async def start(self, on_message: Callable[['MessageFrame'], Awaitable[None]]):
        on_message_tasks = set()

        async with self._client as client:
            while True:
                raw_frame = await client.receive_bytes()

                frame = Frame.from_bytes(raw_frame)
                if frame.is_error:
                    raise FirehoseError(XrpcError(frame.body.error, frame.body.message))
                elif frame.is_message:
                    task = self._loop.create_task(on_message(frame))
                    on_message_tasks.add(task)
                    task.add_done_callback(on_message_tasks.discard)
                else:
                    raise FirehoseError('Unknown frame type')


FirehoseClient = _WebsocketClient
AsyncFirehoseClient = _AsyncWebsocketClient


def _parse_message_body(msg: 'MessageFrame'):
    from atproto import CAR
    from atproto import models
    from atproto.xrpc_client.models.utils import get_or_create_model

    # TODO(MarshalX): Add helper function to match types
    if msg.type == '#commit':
        commit = get_or_create_model(msg.body, models.ComAtprotoSyncSubscribeRepos.Commit)
        commit.blocks = CAR.from_bytes(commit.blocks)
        return commit


def _main_test():
    client = FirehoseClient('com.atproto.sync.subscribeRepos')

    def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, _parse_message_body(message))

    client.start(on_message_handler)


async def _main_async_test():
    client = AsyncFirehoseClient('com.atproto.sync.subscribeRepos')

    async def on_message_handler(message: 'MessageFrame') -> None:
        print('Message', message.header, _parse_message_body(message))
        await asyncio.sleep(0.1)

    await client.start(on_message_handler)


if __name__ == '__main__':
    import asyncio

    _main_test()
    # asyncio.get_event_loop().run_until_complete(_main_async_test())
