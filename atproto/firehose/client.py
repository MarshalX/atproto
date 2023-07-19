import asyncio
import random
import socket
import threading
import time
import traceback
import typing as t
from urllib.parse import urlencode

from websockets.client import connect as aconnect
from websockets.exceptions import (
    ConnectionClosedError,
    ConnectionClosedOK,
    InvalidHandshake,
    PayloadTooBig,
    ProtocolError,
)
from websockets.sync.client import connect

from atproto.exceptions import CBORDecodingError, DAGCBORDecodingError, FirehoseDecodingError, FirehoseError
from atproto.firehose.models import ErrorFrame, Frame, MessageFrame
from atproto.xrpc_client.models.common import XrpcError

_BASE_WEBSOCKET_URI = 'wss://bsky.social/xrpc'
_MAX_MESSAGE_SIZE_BYTES = 1024 * 1024 * 5  # 5MB

OnMessageCallback = t.Callable[['MessageFrame'], t.Generator[t.Any, None, t.Any]]
AsyncOnMessageCallback = t.Callable[['MessageFrame'], t.Coroutine[t.Any, t.Any, t.Any]]

OnCallbackErrorCallback = t.Callable[[BaseException], None]


def _build_websocket_uri(
    method: str, base_uri: t.Optional[str] = None, params: t.Optional[t.Dict[str, t.Any]] = None
) -> str:
    if base_uri is None:
        base_uri = _BASE_WEBSOCKET_URI

    query_string = ''
    if params:
        query_string = f'?{urlencode(params)}'

    return f'{base_uri}/{method}{query_string}'


def _handle_frame_decoding_error(exception: Exception) -> None:
    if isinstance(exception, (CBORDecodingError, DAGCBORDecodingError, FirehoseDecodingError)):
        # Ignore an invalid firehose frame that could not be properly decoded.
        # It's better to ignore one frame rather than stop the whole connection
        # or trap into an infinite loop of reconnections.
        return

    raise exception


def _handle_websocket_error_or_stop(exception: Exception) -> bool:
    """Returns if the connection should be properly being closed or reraise exception."""
    if isinstance(exception, (ConnectionClosedOK,)):
        return True
    if isinstance(exception, (ConnectionClosedError, InvalidHandshake, PayloadTooBig, ProtocolError, socket.gaierror)):
        return False

    raise FirehoseError from exception


class _WebsocketClientBase:
    def __init__(
        self,
        method: str,
        base_url: t.Optional[str] = None,
        params: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        self._url = _build_websocket_uri(method, base_url, params)

        self._reconnect_no = 0
        self._max_reconnect_delay_sec = 64

        self._on_message_callback: t.Optional[t.Union[OnMessageCallback, AsyncOnMessageCallback]] = None
        self._on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None

    def _get_client(self):
        return connect(self._url, max_size=_MAX_MESSAGE_SIZE_BYTES)

    def _get_async_client(self):
        return aconnect(self._url, max_size=_MAX_MESSAGE_SIZE_BYTES)

    def _get_reconnection_delay(self) -> int:
        base_sec = 2**self._reconnect_no
        rand_sec = random.uniform(-0.5, 0.5)  # noqa: S311

        return min(base_sec, self._max_reconnect_delay_sec) + rand_sec

    def _process_raw_frame(self, data: bytes) -> None:
        frame = Frame.from_bytes(data)
        if isinstance(frame, ErrorFrame):
            raise FirehoseError(XrpcError(frame.body.error, frame.body.message))
        if isinstance(frame, MessageFrame):
            self._process_message_frame(frame)
        else:
            raise FirehoseDecodingError('Unknown frame type')

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
        self._on_message_callback = on_message_callback
        self._on_callback_error_callback = on_callback_error_callback

    def stop(self):
        """Unsubscribe and stop the Firehose client.

        Returns:
            :obj:`None`
        """
        raise NotImplementedError

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        raise NotImplementedError


class _WebsocketClient(_WebsocketClientBase):
    def __init__(
        self, method: str, base_url: t.Optional[str] = None, params: t.Optional[t.Dict[str, t.Any]] = None
    ) -> None:
        super().__init__(method, base_url, params)

        self._stop_lock = threading.Lock()

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        try:
            self._on_message_callback(frame)
        except Exception as e:  # noqa: BLE001
            if self._on_callback_error_callback:
                try:
                    self._on_callback_error_callback(e)
                except:  # noqa
                    traceback.print_exc()
            else:
                traceback.print_exc()

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)

        while not self._stop_lock.locked():
            try:
                if self._reconnect_no != 0:
                    time.sleep(self._get_reconnection_delay())

                with self._get_client() as client:
                    self._reconnect_no = 0

                    while not self._stop_lock.locked():
                        raw_frame = client.recv()
                        if isinstance(raw_frame, str):
                            # skip text frames (should not be occurred)
                            continue

                        try:
                            self._process_raw_frame(raw_frame)
                        except Exception as e:  # noqa: BLE001
                            _handle_frame_decoding_error(e)
            except Exception as e:  # noqa: BLE001
                self._reconnect_no += 1

                should_stop = _handle_websocket_error_or_stop(e)
                if should_stop:
                    break

        if self._stop_lock.locked():
            self._stop_lock.release()

    def stop(self):
        if not self._stop_lock.locked():
            self._stop_lock.acquire()


class _AsyncWebsocketClient(_WebsocketClientBase):
    def __init__(
        self, method: str, base_url: t.Optional[str] = None, params: t.Optional[t.Dict[str, t.Any]] = None
    ) -> None:
        super().__init__(method, base_url, params)

        self._loop = asyncio.get_event_loop()
        self._on_message_tasks: t.Set[asyncio.Task] = set()

        self._stop_lock = asyncio.Lock()

    def _on_message_callback_done(self, task: asyncio.Task) -> None:
        self._on_message_tasks.discard(task)

        exception = task.exception()
        if exception:
            if not self._on_callback_error_callback:
                traceback.print_exc()
                return

            try:
                self._on_callback_error_callback(exception)
            except:  # noqa
                traceback.print_exc()

    def _process_message_frame(self, frame: 'MessageFrame') -> None:
        task: asyncio.Task = self._loop.create_task(self._on_message_callback(frame))
        self._on_message_tasks.add(task)
        task.add_done_callback(self._on_message_callback_done)

    async def start(self, *args, **kwargs):
        super().start(*args, **kwargs)

        while not self._stop_lock.locked():
            try:
                if self._reconnect_no != 0:
                    await asyncio.sleep(self._get_reconnection_delay())

                async with self._get_async_client() as client:
                    self._reconnect_no = 0

                    while not self._stop_lock.locked():
                        raw_frame = await client.recv()
                        if isinstance(raw_frame, str):
                            # skip text frames (should not be occurred)
                            continue

                        try:
                            self._process_raw_frame(raw_frame)
                        except Exception as e:  # noqa: BLE001
                            _handle_frame_decoding_error(e)
            except Exception as e:  # noqa: BLE001
                self._reconnect_no += 1

                should_stop = _handle_websocket_error_or_stop(e)
                if should_stop:
                    break

        if self._stop_lock.locked():
            self._stop_lock.release()

    async def stop(self):
        if not self._stop_lock.locked():
            await self._stop_lock.acquire()


FirehoseClient = _WebsocketClient
AsyncFirehoseClient = _AsyncWebsocketClient
