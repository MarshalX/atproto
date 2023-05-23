import asyncio
import random
import threading
import time
import traceback
import typing as t

import httpx
from httpx_ws import (
    WebSocketDisconnect,
    WebSocketInvalidTypeReceived,
    WebSocketNetworkError,
    WebSocketUpgradeError,
    aconnect_ws,
    connect_ws,
)

from atproto.exceptions import FirehoseError
from atproto.firehose.models import Frame
from atproto.xrpc_client.models.common import XrpcError

if t.TYPE_CHECKING:
    from atproto.firehose.models import MessageFrame

_BASE_WEBSOCKET_URL = 'https://bsky.social/xrpc'

OnMessageCallback = t.Callable[['MessageFrame'], None]
AsyncOnMessageCallback = t.Callable[['MessageFrame'], t.Awaitable[None]]

OnCallbackErrorCallback = t.Callable[[BaseException], None]


def _build_websocket_url(method: str, base_url: t.Optional[str] = None) -> str:
    if base_url is None:
        base_url = _BASE_WEBSOCKET_URL

    return f'{base_url}/{method}'


def _handle_firehose_error_or_stop(exception: Exception) -> bool:
    """Returns if the connection should be properly be closed or reraise exception."""

    print(exception)
    if isinstance(exception, WebSocketDisconnect):
        if exception.code == 1000:
            return True
        elif exception.code in {1001, 1002, 1003}:
            return False
    elif isinstance(exception, WebSocketNetworkError):
        return False
    elif isinstance(exception, httpx.NetworkError):
        return False
    elif isinstance(exception, httpx.TimeoutException):
        return False
    elif isinstance(exception, WebSocketInvalidTypeReceived):
        raise FirehoseError from exception
    elif isinstance(exception, WebSocketUpgradeError):
        raise FirehoseError from exception
    elif isinstance(exception, FirehoseError):
        raise exception

    raise FirehoseError from exception


class _WebsocketClientBase:
    def __init__(
        self,
        method: str,
        base_url: t.Optional[str] = None,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        *,
        async_version=False,
    ):
        self._params = params
        self._url = _build_websocket_url(method, base_url)

        self._async_version = async_version

        self._reconnect_no = 0
        self._max_reconnect_delay_sec = 64

        self._on_message_callback: t.Optional[t.Union[OnMessageCallback, AsyncOnMessageCallback]] = None
        self._on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None

    def _get_client(self):
        if self._async_version:
            return aconnect_ws(self._url, params=self._params)

        return connect_ws(self._url, params=self._params)

    def _get_reconnection_delay(self) -> int:
        base_sec = 2**self._reconnect_no
        rand_sec = random.uniform(-0.5, 0.5)

        return min(base_sec, self._max_reconnect_delay_sec) + rand_sec

    def _process_raw_frame(self, data: bytes) -> None:
        frame = Frame.from_bytes(data)
        if frame.is_error:
            raise FirehoseError(XrpcError(frame.body.error, frame.body.message))
        elif frame.is_message:
            self._process_message_frame(frame)
        else:
            raise FirehoseError('Unknown frame type')

    def start(
        self,
        on_message_callback: t.Union[OnMessageCallback, AsyncOnMessageCallback],
        on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None,
    ) -> None:
        """Subscribe to Firehose and start client.

        Args:
            on_message_callback: Callback that will be called on the new Firehose message.
            on_callback_error_callback: Callback that will be called if the `on_message_callback` raised an exception.

        Returns:
            :obj:`None`
        """
        raise NotImplemented

    def stop(self) -> None:
        """Unsubscribe and stop Firehose client.

        Returns:
            :obj:`None`
        """
        raise NotImplemented

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        raise NotImplemented


class _WebsocketClient(_WebsocketClientBase):
    def __init__(self, method: str, base_url: t.Optional[str] = None, params: t.Optional[t.Dict[str, t.Any]] = None):
        super().__init__(method, base_url, params)

        self._stop_lock = threading.Lock()

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        try:
            self._on_message_callback(frame)
        except Exception as e:  # noqa
            if self._on_callback_error_callback:
                try:
                    self._on_callback_error_callback(e)
                except Exception:  # noqa
                    traceback.print_exc()
            else:
                traceback.print_exc()

    def start(
        self,
        on_message_callback: OnMessageCallback,
        on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None,
    ) -> None:
        self._on_message_callback = on_message_callback
        self._on_callback_error_callback = on_callback_error_callback

        while not self._stop_lock.locked():
            try:
                if self._reconnect_no != 0:
                    time.sleep(self._get_reconnection_delay())

                with self._get_client() as client:
                    self._reconnect_no = 0

                    while not self._stop_lock.locked():
                        raw_frame = client.receive_bytes()
                        self._process_raw_frame(raw_frame)
            except Exception as e:
                self._reconnect_no += 1

                should_stop = _handle_firehose_error_or_stop(e)
                if should_stop:
                    break

        self._stop_lock.release()

    def stop(self):
        if not self._stop_lock.locked():
            self._stop_lock.acquire()


class _AsyncWebsocketClient(_WebsocketClientBase):
    def __init__(self, method: str, base_url: t.Optional[str] = None, params: t.Optional[t.Dict[str, t.Any]] = None):
        super().__init__(method, base_url, params, async_version=True)

        self._loop = asyncio.get_event_loop()
        self._on_message_tasks = set()

        self._stop_lock = asyncio.Lock()

    def _on_message_callback_done(self, task: asyncio.Task) -> None:
        self._on_message_tasks.discard(task)

        if task.exception():
            if not self._on_callback_error_callback:
                traceback.print_exc()
                return

            try:
                self._on_callback_error_callback(task.exception())
            except Exception:  # noqa
                traceback.print_exc()

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        task = self._loop.create_task(self._on_message_callback(frame))
        self._on_message_tasks.add(task)
        task.add_done_callback(self._on_message_callback_done)

    async def start(
        self,
        on_message_callback: AsyncOnMessageCallback,
        on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None,
    ) -> None:
        self._on_message_callback = on_message_callback
        self._on_callback_error_callback = on_callback_error_callback

        while not self._stop_lock.locked():
            try:
                if self._reconnect_no != 0:
                    await asyncio.sleep(self._get_reconnection_delay())

                async with self._get_client() as client:
                    self._reconnect_no = 0

                    while not self._stop_lock.locked():
                        raw_frame = await client.receive_bytes()
                        self._process_raw_frame(raw_frame)
            except Exception as e:
                self._reconnect_no += 1

                should_stop = _handle_firehose_error_or_stop(e)
                if should_stop:
                    break

        self._stop_lock.release()

    async def stop(self):
        if not self._stop_lock.locked():
            await self._stop_lock.acquire()


FirehoseClient = _WebsocketClient
AsyncFirehoseClient = _AsyncWebsocketClient
