import asyncio
import contextlib
import random
import time
import traceback
import typing as t
from copy import deepcopy
from urllib.parse import urlencode

from atproto_core.exceptions import AtProtocolError
from websockets.asyncio.client import connect as aconnect
from websockets.exceptions import (
    ConnectionClosedError,
    ConnectionClosedOK,
    InvalidHandshake,
    PayloadTooBig,
    ProtocolError,
)
from websockets.sync.client import connect

_HEALTHY_CONNECTION_SEC = 60

_OK_ERRORS = (ConnectionClosedOK,)
#: Errors that mean "this connection is gone, get a new one" rather than "give up".
_ERR_ERRORS = (
    # OSError covers TimeoutError, ConnectionError, ssl.SSLError, socket.gaierror and socket.herror
    OSError,
    asyncio.TimeoutError,  # a plain Exception before Python 3.11, an OSError from 3.11 on
    ConnectionClosedError,
    InvalidHandshake,
    PayloadTooBig,
    ProtocolError,
)

if t.TYPE_CHECKING:
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketClient
    from websockets.asyncio.client import connect as AsyncConnect
    from websockets.sync.client import ClientConnection as SyncWebSocketClient

#: A decoded frame. Its type is defined by the subclass.
Frame = t.Any

OnMessageCallback = t.Callable[[Frame], None]
AsyncOnMessageCallback = t.Callable[[Frame], t.Coroutine[t.Any, t.Any, None]]

OnCallbackErrorCallback = t.Callable[[BaseException], None]
AsyncOnCallbackErrorCallback = t.Callable[[BaseException], t.Coroutine[t.Any, t.Any, None]]


def build_websocket_uri(method: str, base_uri: str, params: t.Optional[t.Dict[str, t.Any]] = None) -> str:
    """Build an XRPC subscription URI.

    Args:
        method: NSID of the subscription.
        base_uri: Base websocket URI.
        params: Query params.

    Returns:
        :obj:`str`: Websocket URI.
    """
    query_string = ''
    if params:
        query_string = f'?{urlencode(params, doseq=True)}'

    return f'{base_uri}/{method}{query_string}'


class WebsocketClientBase:
    """Base of the reconnecting websocket clients.

    Subclasses own frame decoding; this class owns the connection lifecycle.
    """

    #: Exception type used to wrap unexpected failures.
    _error_class: t.Type[AtProtocolError] = AtProtocolError

    def __init__(
        self,
        method: str,
        base_uri: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        recv_timeout: t.Optional[float] = None,
        max_message_size_bytes: t.Optional[int] = None,
        subprotocols: t.Optional[t.Sequence[str]] = None,
    ) -> None:
        self._method = method
        self._base_uri = base_uri
        self._params = params
        self._recv_timeout = recv_timeout
        self._max_message_size_bytes = max_message_size_bytes
        self._subprotocols = subprotocols

        self._reconnect_no = 0
        self._max_reconnect_delay_sec = 64

    def _decode_frame(self, raw_frame: t.Union[str, bytes]) -> t.Optional[Frame]:
        """Decode a raw websocket frame. Return :obj:`None` to skip it."""
        raise NotImplementedError

    def _handle_frame_decoding_error(self, exception: Exception) -> None:
        """Swallow a tolerable decoding error or reraise it."""
        raise NotImplementedError

    def _handle_websocket_error_or_stop(self, exception: Exception) -> bool:
        """Return if the connection should be properly being closed or reraise exception."""
        if isinstance(exception, _OK_ERRORS):
            return True
        if isinstance(exception, _ERR_ERRORS):
            return False

        if isinstance(exception, self._error_class):
            raise exception

        raise self._error_class(exception) from exception

    def update_params(self, params: t.Dict[str, t.Any]) -> None:
        """Update params.

        Args:
            params: Query params.

        Returns:
            :obj:`None`
        """
        self._params = deepcopy(params)

    @property
    def _websocket_uri(self) -> str:
        return build_websocket_uri(self._method, self._base_uri, self._params)

    def _get_connect_kwargs(self) -> t.Dict[str, t.Any]:
        kwargs: t.Dict[str, t.Any] = {'max_size': self._max_message_size_bytes, 'close_timeout': 0.1}
        if self._subprotocols:
            kwargs['subprotocols'] = list(self._subprotocols)

        return kwargs

    def _get_client(self) -> 'SyncWebSocketClient':
        return connect(self._websocket_uri, **self._get_connect_kwargs())

    def _get_async_client(self) -> 'AsyncConnect':
        # Async client connect function accepts ping_interval directly (default is 20s)
        return aconnect(self._websocket_uri, **self._get_connect_kwargs())

    def _get_reconnection_delay(self) -> float:
        base_sec = 2**self._reconnect_no
        rand_sec = random.uniform(-0.5, 0.5)  # noqa: S311

        return min(base_sec, self._max_reconnect_delay_sec) + rand_sec

    def _track_reconnection(self, connected_at: t.Optional[float]) -> None:
        """Escalate the backoff, unless the connection that just died had been healthy.

        Args:
            connected_at: When the connection was established, or :obj:`None` if it never was.
        """
        if connected_at is not None and time.monotonic() - connected_at >= _HEALTHY_CONNECTION_SEC:
            # Start over from the base delay rather than reconnecting instantly: when a server
            # restarts it drops every client at once, and they must not all come back together.
            self._reconnect_no = 1
        else:
            self._reconnect_no += 1


class WebsocketClient(WebsocketClientBase):
    """Reconnecting synchronous websocket client."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._stopped = False
        self._client: t.Optional[SyncWebSocketClient] = None

        self._on_message_callback: t.Optional[OnMessageCallback] = None
        self._on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None

    def _before_connect(self) -> None:
        """Prepare the next connection. Called before every dial, including reconnects."""

    def _process_frame(self, frame: Frame) -> None:
        try:
            if self._on_message_callback is not None:
                self._on_message_callback(frame)
        except Exception as e:  # noqa: BLE001
            if self._on_callback_error_callback:
                try:
                    self._on_callback_error_callback(e)
                except:  # noqa
                    traceback.print_exc()
            else:
                traceback.print_exc()

    def start(
        self,
        on_message_callback: OnMessageCallback,
        on_callback_error_callback: t.Optional[OnCallbackErrorCallback] = None,
    ) -> None:
        """Subscribe and start the client.

        Args:
            on_message_callback: Callback that will be called on the new message.
            on_callback_error_callback: Callback that will be called if the `on_message_callback` raised an exception.

        Returns:
            :obj:`None`
        """
        self._on_message_callback = on_message_callback
        self._on_callback_error_callback = on_callback_error_callback

        while not self._stopped:
            connected_at = None
            try:
                if self._reconnect_no != 0:
                    time.sleep(self._get_reconnection_delay())

                self._before_connect()
                client = self._get_client()
                with client:
                    connected_at = time.monotonic()
                    self._client = client

                    while not self._stopped:
                        raw_frame = client.recv(self._recv_timeout)

                        try:
                            frame = self._decode_frame(raw_frame)
                            if frame is not None:
                                self._process_frame(frame)
                        except Exception as e:  # noqa: BLE001
                            self._handle_frame_decoding_error(e)
            except Exception as e:  # noqa: BLE001
                self._track_reconnection(connected_at)

                should_stop = self._handle_websocket_error_or_stop(e)
                if should_stop:
                    break
            finally:
                self._client = None

    def stop(self) -> None:
        """Unsubscribe and stop the client.

        Safe to call from another thread. The client stops even if it is currently waiting for
        the next frame on an idle connection.

        Returns:
            :obj:`None`
        """
        self._stopped = True

        client = self._client
        if client is not None:
            with contextlib.suppress(Exception):
                client.close()


class AsyncWebsocketClient(WebsocketClientBase):
    """Reconnecting asynchronous websocket client."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        self._stop_event = asyncio.Event()
        self._client: t.Optional[AsyncWebSocketClient] = None

        self._on_message_callback: t.Optional[AsyncOnMessageCallback] = None
        self._on_callback_error_callback: t.Optional[AsyncOnCallbackErrorCallback] = None

    async def _before_connect(self) -> None:
        """Prepare the next connection. Called before every dial, including reconnects."""

    async def _process_frame(self, frame: Frame) -> None:
        try:
            if self._on_message_callback is not None:
                await self._on_message_callback(frame)
        except Exception as e:  # noqa: BLE001
            if self._on_callback_error_callback:
                try:
                    await self._on_callback_error_callback(e)
                except:  # noqa
                    traceback.print_exc()
            else:
                traceback.print_exc()

    async def start(
        self,
        on_message_callback: AsyncOnMessageCallback,
        on_callback_error_callback: t.Optional[AsyncOnCallbackErrorCallback] = None,
    ) -> None:
        """Subscribe and start the client.

        Args:
            on_message_callback: Callback that will be called on the new message.
            on_callback_error_callback: Callback that will be called if the `on_message_callback` raised an exception.

        Returns:
            :obj:`None`
        """
        self._on_message_callback = on_message_callback
        self._on_callback_error_callback = on_callback_error_callback

        while not self._stop_event.is_set():
            connected_at = None
            try:
                if self._reconnect_no != 0:
                    await asyncio.sleep(self._get_reconnection_delay())

                await self._before_connect()
                async with self._get_async_client() as client:
                    connected_at = time.monotonic()
                    self._client = client

                    while not self._stop_event.is_set():
                        # TODO(MarshalX): if the perf will be critical consider to use async-timeout lib
                        raw_frame = await asyncio.wait_for(client.recv(), timeout=self._recv_timeout)

                        try:
                            frame = self._decode_frame(raw_frame)
                            if frame is not None:
                                await self._process_frame(frame)
                        except Exception as e:  # noqa: BLE001
                            self._handle_frame_decoding_error(e)

            except Exception as e:  # noqa: BLE001
                self._track_reconnection(connected_at)

                should_stop = self._handle_websocket_error_or_stop(e)
                if should_stop:
                    break
            finally:
                self._client = None

    async def stop(self) -> None:
        """Unsubscribe and stop the client.

        Safe to call from another task. The client stops even if it is currently waiting for
        the next frame on an idle connection.

        Returns:
            :obj:`None`
        """
        self._stop_event.set()

        client = self._client
        if client is not None:
            with contextlib.suppress(Exception):
                await client.close()
