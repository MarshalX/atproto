import asyncio
import base64
import concurrent.futures
import contextlib
import json
import queue
import secrets
import threading
import typing

import httpcore
import httpx
import wsproto
from httpcore import AsyncNetworkStream, NetworkStream
from typing_extensions import Literal
from wsproto.connection import CloseReason

from atproto.ws_client._ping import AsyncPingManager, PingManager

JSONMode = Literal['text', 'binary']
TaskFunction = typing.TypeVar('TaskFunction')
TaskResult = typing.TypeVar('TaskResult')

DEFAULT_MAX_MESSAGE_SIZE_BYTES = 65_536
DEFAULT_QUEUE_SIZE = 512
DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS = 20.0
DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS = 20.0


class HTTPXWSException(Exception):
    """
    Base exception class for HTTPX WS.
    """


class WebSocketUpgradeError(HTTPXWSException):
    """
    Raised when the initial connection didn't correctly upgrade to a WebSocket session.
    """

    def __init__(self, response: httpx.Response) -> None:
        self.response = response


class WebSocketDisconnect(HTTPXWSException):
    """
    Raised when the server closed the WebSocket session.

    Args:
        code:
            The integer close code to indicate why the connection has closed.
        reason:
            Additional reasoning for why the connection has closed.
    """

    def __init__(self, code: int = 1000, reason: typing.Optional[str] = None) -> None:
        self.code = code
        self.reason = reason or ''


class WebSocketInvalidTypeReceived(HTTPXWSException):
    """
    Raised when a event is not of the expected type.
    """

    def __init__(self, event: wsproto.events.Event) -> None:
        self.event = event


class WebSocketNetworkError(HTTPXWSException):
    """
    Raised when a network error occured,
    typically if the underlying stream has closed or timeout.
    """


class ShouldClose(Exception):
    pass


class WebSocketSession:
    """
    Sync helper representing an opened WebSocket session.

    Attributes:
        subprotocol (typing.Optional[str]):
            Optional protocol that has been accepted by the server.
    """

    subprotocol: typing.Optional[str]

    def __init__(
        self,
        stream: NetworkStream,
        *,
        max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
        keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
        subprotocol: typing.Optional[str] = None,
    ) -> None:
        self.stream = stream
        self.connection = wsproto.Connection(wsproto.ConnectionType.CLIENT)
        self.subprotocol = subprotocol

        self._events: queue.Queue[typing.Union[wsproto.events.Event, HTTPXWSException]] = queue.Queue(queue_size)

        self._ping_manager = PingManager()

        self._should_close = threading.Event()

        self._background_receive_task = threading.Thread(
            target=self._background_receive, args=(max_message_size_bytes,)
        )
        self._background_receive_task.start()

        self._background_keepalive_ping_task: typing.Optional[threading.Thread] = None
        if keepalive_ping_interval_seconds is not None:
            self._background_keepalive_ping_task = threading.Thread(
                target=self._background_keepalive_ping,
                args=(keepalive_ping_interval_seconds, keepalive_ping_timeout_seconds),
            )
            self._background_keepalive_ping_task.start()

    def ping(self, payload: bytes = b'') -> threading.Event:
        """
        Send a Ping message.

        Args:
            payload:
                Payload to attach to the Ping event.
                Internally, it's used to track this specific event.
                If left empty, a random one will be generated.

        Returns:
            An event that can be used to wait for the corresponding Pong response.

        Examples:
            Send a Ping and wait for the Pong

                pong_callback = ws.ping()
                # Will block until the corresponding Pong is received.
                pong_callback.wait()
        """
        ping_id, callback = self._ping_manager.create(payload)
        event = wsproto.events.Ping(ping_id)
        self.send(event)
        return callback

    def send(self, event: wsproto.events.Event) -> None:
        """
        Send an Event message.

        Mainly useful to send events that are not supported by the library.
        Most of the time, [ping()][ws_client.WebSocketSession.ping],
        [send_text()][ws_client.WebSocketSession.send_text],
        [send_bytes()][ws_client.WebSocketSession.send_bytes]
        and [send_json()][ws_client.WebSocketSession.send_json] are preferred.

        Args:
            event: The event to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send an event.

                event = wsproto.events.Message(b"Hello!")
                ws.send(event)
        """
        try:
            data = self.connection.send(event)
            self.stream.write(data)
        except httpcore.WriteError as e:
            self.close(CloseReason.INTERNAL_ERROR, 'Stream write error')
            raise WebSocketNetworkError from e

    def send_text(self, data: str) -> None:
        """
        Send a text message.

        Args:
            data: The text to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send a text message.

                ws.send_text("Hello!")
        """
        event = wsproto.events.TextMessage(data=data)
        self.send(event)

    def send_bytes(self, data: bytes) -> None:
        """
        Send a bytes message.

        Args:
            data: The data to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send a bytes message.

                ws.send_bytes(b"Hello!")
        """
        event = wsproto.events.BytesMessage(data=data)
        self.send(event)

    def send_json(self, data: typing.Any, mode: JSONMode = 'text') -> None:
        """
        Send JSON data.

        Args:
            data:
                The data to send. Must be serializable by [json.dumps][json.dumps].
            mode:
                The sending mode. Should either be `'text'` or `'bytes'`.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send JSON data.

                data = {"message": "Hello!"}
                ws.send_json(data)
        """
        if mode not in ['text', 'binary']:
            raise ValueError(f'Invalid mode: {mode}')

        serialized_data = json.dumps(data)
        if mode == 'text':
            self.send_text(serialized_data)
        else:
            self.send_bytes(serialized_data.encode('utf-8'))

    def receive(self, timeout: typing.Optional[float] = None) -> wsproto.events.Event:
        """
        Receive an event from the server.

        Mainly useful to receive raw [wsproto.events.Event][wsproto.events.Event].
        Most of the time, [receive_text()][ws_client.WebSocketSession.receive_text],
        [receive_bytes()][ws_client.WebSocketSession.receive_bytes],
        and [receive_json()][ws_client.WebSocketSession.receive_json] are preferred.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            A raw [wsproto.events.Event][wsproto.events.Event].

        Raises:
            queue.Empty: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.

        Examples:
            Wait for an event until one is available.

                try:
                    event = ws.receive()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for an event for 2 seconds.

                try:
                    event = ws.receive(timeout=2.)
                except queue.Empty:
                    print("No event received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = self._events.get(block=True, timeout=timeout)
        if isinstance(event, HTTPXWSException):
            raise event
        if isinstance(event, wsproto.events.CloseConnection):
            raise WebSocketDisconnect(event.code, event.reason)
        return event

    def receive_text(self, timeout: typing.Optional[float] = None) -> str:
        """
        Receive text from the server.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            Text data.

        Raises:
            queue.Empty: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event was not a text message.

        Examples:
            Wait for text until available.

                try:
                    text = ws.receive_text()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for text for 2 seconds.

                try:
                    event = ws.receive_text(timeout=2.)
                except queue.Empty:
                    print("No text received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = self.receive(timeout)
        if isinstance(event, wsproto.events.TextMessage):
            return event.data
        raise WebSocketInvalidTypeReceived(event)

    def receive_bytes(self, timeout: typing.Optional[float] = None) -> bytes:
        """
        Receive bytes from the server.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            Bytes data.

        Raises:
            queue.Empty: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event was not a bytes message.

        Examples:
            Wait for bytes until available.

                try:
                    data = ws.receive_bytes()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for bytes for 2 seconds.

                try:
                    data = ws.receive_bytes(timeout=2.)
                except queue.Empty:
                    print("No data received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = self.receive(timeout)
        if isinstance(event, wsproto.events.BytesMessage):
            return event.data
        raise WebSocketInvalidTypeReceived(event)

    def receive_json(self, timeout: typing.Optional[float] = None, mode: JSONMode = 'text') -> typing.Any:
        """
        Receive JSON data from the server.

        The received data should be parseable by [json.loads][json.loads].

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.
            mode:
                Receive mode. Should either be `'text'` or `'bytes'`.

        Returns:
            Parsed JSON data.

        Raises:
            queue.Empty: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event
                didn't correspond to the specified mode.

        Examples:
            Wait for data until available.

                try:
                    data = ws.receive_json()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for data for 2 seconds.

                try:
                    data = ws.receive_json(timeout=2.)
                except queue.Empty:
                    print("No data received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        if mode not in ['text', 'binary']:
            raise ValueError(f'Invalid mode: {mode}')

        data: typing.Union[str, bytes]
        if mode == 'text':
            data = self.receive_text(timeout)
        elif mode == 'binary':
            data = self.receive_bytes(timeout)
        return json.loads(data)

    def close(self, code: int = 1000, reason: typing.Optional[str] = None):
        """
        Close the WebSocket session.

        Internally, it'll send the
        [CloseConnection][wsproto.events.CloseConnection] event.

        Args:
            code:
                The integer close code to indicate why the connection has closed.
            reason:
                Additional reasoning for why the connection has closed.

        Examples:
            Close the WebSocket session.

                ws.close()
        """
        self._should_close.set()
        if self.connection.state not in {
            wsproto.connection.ConnectionState.LOCAL_CLOSING,
            wsproto.connection.ConnectionState.CLOSED,
        }:
            event = wsproto.events.CloseConnection(code, reason)
            data = self.connection.send(event)
            with contextlib.suppress(httpcore.WriteError):
                self.stream.write(data)

        self.stream.close()

    def _background_receive(self, max_bytes: int) -> None:
        """
        Background thread listening for data from the server.

        Internally, it'll:

        * Answer to Ping events.
        * Acknowledge Pong events.
        * Put other events in the [_events][_events]
        queue that'll eventually be consumed by the user.

        Args:
            max_bytes: The maximum chunk size to read at each iteration.
        """
        try:
            while not self._should_close.is_set():
                data = self._wait_until_closed(self.stream.read, max_bytes)
                self.connection.receive_data(data)
                for event in self.connection.events():
                    if isinstance(event, wsproto.events.Ping):
                        data = self.connection.send(event.response())
                        self.stream.write(data)
                        continue
                    if isinstance(event, wsproto.events.Pong):
                        self._ping_manager.ack(event.payload)
                        continue
                    if isinstance(event, wsproto.events.CloseConnection):
                        self._should_close.set()
                    self._events.put(event)
        except (httpcore.ReadError, httpcore.WriteError):
            self.close(CloseReason.INTERNAL_ERROR, 'Stream error')
            self._events.put(WebSocketNetworkError())
        except ShouldClose:
            pass

    def _background_keepalive_ping(
        self, interval_seconds: float, timeout_seconds: typing.Optional[float] = None
    ) -> None:
        try:
            while not self._should_close.is_set():
                should_close = self._wait_until_closed(self._should_close.wait, interval_seconds)
                if should_close:
                    raise ShouldClose
                pong_callback = self.ping()
                if timeout_seconds is not None:
                    acknowledged = self._wait_until_closed(pong_callback.wait, timeout_seconds)
                    if not acknowledged:
                        self.close(CloseReason.INTERNAL_ERROR, 'Keepalive ping timeout')
                        self._events.put(WebSocketNetworkError())
        except ShouldClose:
            pass

    def _wait_until_closed(self, callable: typing.Callable[..., TaskResult], *args, **kwargs) -> TaskResult:
        try:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
            wait_close_task = executor.submit(self._should_close.wait)
            todo_task = executor.submit(callable, *args, **kwargs)
        except RuntimeError as e:
            raise ShouldClose from e
        done, pending = concurrent.futures.wait(
            (todo_task, wait_close_task), return_when=concurrent.futures.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        if wait_close_task in done and todo_task not in done:
            raise ShouldClose
        result = todo_task.result()
        executor.shutdown(False)
        return result


class AsyncWebSocketSession:
    """
    Async helper representing an opened WebSocket session.

    Attributes:
        subprotocol (typing.Optional[str]):
            Optional protocol that has been accepted by the server.
    """

    subprotocol: typing.Optional[str]

    def __init__(
        self,
        stream: AsyncNetworkStream,
        *,
        max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
        keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
        subprotocol: typing.Optional[str] = None,
    ) -> None:
        self.stream = stream
        self.connection = wsproto.Connection(wsproto.ConnectionType.CLIENT)
        self.subprotocol = subprotocol

        self._events: asyncio.Queue[typing.Union[wsproto.events.Event, HTTPXWSException]] = asyncio.Queue(queue_size)

        self._ping_manager = AsyncPingManager()

        self._should_close = asyncio.Event()

        self._background_receive_task = asyncio.create_task(self._background_receive(max_message_size_bytes))

        self._background_keepalive_ping_task: typing.Optional[asyncio.Task] = None
        if keepalive_ping_interval_seconds is not None:
            self._background_keepalive_ping_task = asyncio.create_task(
                self._background_keepalive_ping(keepalive_ping_interval_seconds, keepalive_ping_timeout_seconds)
            )

    async def ping(self, payload: bytes = b'') -> asyncio.Event:
        """
        Send a Ping message.

        Args:
            payload:
                Payload to attach to the Ping event.
                Internally, it's used to track this specific event.
                If left empty, a random one will be generated.

        Returns:
            An event that can be used to wait for the corresponding Pong response.

        Examples:
            Send a Ping and wait for the Pong

                pong_callback = await ws.ping()
                # Will block until the corresponding Pong is received.
                await pong_callback.wait()
        """
        ping_id, callback = self._ping_manager.create(payload)
        event = wsproto.events.Ping(ping_id)
        await self.send(event)
        return callback

    async def send(self, event: wsproto.events.Event) -> None:
        """
        Send an Event message.

        Mainly useful to send events that are not supported by the library.
        Most of the time, [ping()][ws_client.AsyncWebSocketSession.ping],
        [send_text()][ws_client.AsyncWebSocketSession.send_text],
        [send_bytes()][ws_client.AsyncWebSocketSession.send_bytes]
        and [send_json()][ws_client.AsyncWebSocketSession.send_json] are preferred.

        Args:
            event: The event to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send an event.

                event = await wsproto.events.Message(b"Hello!")
                ws.send(event)
        """
        try:
            data = self.connection.send(event)
            await self.stream.write(data)
        except httpcore.WriteError as e:
            await self.close(CloseReason.INTERNAL_ERROR, 'Stream write error')
            raise WebSocketNetworkError from e

    async def send_text(self, data: str) -> None:
        """
        Send a text message.

        Args:
            data: The text to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send a text message.

                await ws.send_text("Hello!")
        """
        event = wsproto.events.TextMessage(data=data)
        await self.send(event)

    async def send_bytes(self, data: bytes) -> None:
        """
        Send a bytes message.

        Args:
            data: The data to send.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send a bytes message.

                await ws.send_bytes(b"Hello!")
        """
        event = wsproto.events.BytesMessage(data=data)
        await self.send(event)

    async def send_json(self, data: typing.Any, mode: JSONMode = 'text') -> None:
        """
        Send JSON data.

        Args:
            data:
                The data to send. Must be serializable by [json.dumps][json.dumps].
            mode:
                The sending mode. Should either be `'text'` or `'bytes'`.

        Raises:
            WebSocketNetworkError: A network error occured.

        Examples:
            Send JSON data.

                data = {"message": "Hello!"}
                await ws.send_json(data)
        """
        if mode not in ['text', 'binary']:
            raise ValueError(f'Invalid mode: {mode}')
        serialized_data = json.dumps(data)
        if mode == 'text':
            await self.send_text(serialized_data)
        else:
            await self.send_bytes(serialized_data.encode('utf-8'))

    async def receive(self, timeout: typing.Optional[float] = None) -> wsproto.events.Event:
        """
        Receive an event from the server.

        Mainly useful to receive raw [wsproto.events.Event][wsproto.events.Event].
        Most of the time, [receive_text()][ws_client.AsyncWebSocketSession.receive_text],
        [receive_bytes()][ws_client.AsyncWebSocketSession.receive_bytes],
        and [receive_json()][ws_client.AsyncWebSocketSession.receive_json] are preferred.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            A raw [wsproto.events.Event][wsproto.events.Event].

        Raises:
            asyncio.TimeoutError: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.

        Examples:
            Wait for an event until one is available.

                try:
                    event = await ws.receive()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for an event for 2 seconds.

                try:
                    event = await ws.receive(timeout=2.)
                except asyncio.TimeoutError:
                    print("No event received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = await asyncio.wait_for(self._events.get(), timeout)
        if isinstance(event, HTTPXWSException):
            raise event
        if isinstance(event, wsproto.events.CloseConnection):
            raise WebSocketDisconnect(event.code, event.reason)
        return event

    async def receive_text(self, timeout: typing.Optional[float] = None) -> str:
        """
        Receive text from the server.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            Text data.

        Raises:
            asyncio.TimeoutError: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event was not a text message.

        Examples:
            Wait for text until available.

                try:
                    text = await ws.receive_text()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for text for 2 seconds.

                try:
                    event = await ws.receive_text(timeout=2.)
                except asyncio.TimeoutError:
                    print("No text received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = await self.receive(timeout)
        if isinstance(event, wsproto.events.TextMessage):
            return event.data
        raise WebSocketInvalidTypeReceived(event)

    async def receive_bytes(self, timeout: typing.Optional[float] = None) -> bytes:
        """
        Receive bytes from the server.

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.

        Returns:
            Bytes data.

        Raises:
            asyncio.TimeoutError: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event was not a bytes message.

        Examples:
            Wait for bytes until available.

                try:
                    data = await ws.receive_bytes()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for bytes for 2 seconds.

                try:
                    data = await ws.receive_bytes(timeout=2.)
                except asyncio.TimeoutError:
                    print("No data received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        event = await self.receive(timeout)
        if isinstance(event, wsproto.events.BytesMessage):
            return event.data
        raise WebSocketInvalidTypeReceived(event)

    async def receive_json(self, timeout: typing.Optional[float] = None, mode: JSONMode = 'text') -> typing.Any:
        """
        Receive JSON data from the server.

        The received data should be parseable by [json.loads][json.loads].

        Args:
            timeout:
                Number of seconds to wait for an event.
                If `None`, will block until an event is available.
            mode:
                Receive mode. Should either be `'text'` or `'bytes'`.

        Returns:
            Parsed JSON data.

        Raises:
            asyncio.TimeoutError: No event was received before the timeout delay.
            WebSocketDisconnect: The server closed the websocket.
            WebSocketNetworkError: A network error occured.
            WebSocketInvalidTypeReceived: The received event
                didn't correspond to the specified mode.

        Examples:
            Wait for data until available.

                try:
                    data = await ws.receive_json()
                except WebSocketDisconnect:
                    print("Connection closed")

            Wait for data for 2 seconds.

                try:
                    data = await ws.receive_json(timeout=2.)
                except asyncio.TimeoutError:
                    print("No data received.")
                except WebSocketDisconnect:
                    print("Connection closed")
        """
        if mode not in ['text', 'binary']:
            raise ValueError(f'Invalid mode: {mode}')

        data: typing.Union[str, bytes]
        if mode == 'text':
            data = await self.receive_text(timeout)
        elif mode == 'binary':
            data = await self.receive_bytes(timeout)
        return json.loads(data)

    async def close(self, code: int = 1000, reason: typing.Optional[str] = None):
        """
        Close the WebSocket session.

        Internally, it'll send the
        [CloseConnection][wsproto.events.CloseConnection] event.

        Args:
            code:
                The integer close code to indicate why the connection has closed.
            reason:
                Additional reasoning for why the connection has closed.

        Examples:
            Close the WebSocket session.

                await ws.close()
        """
        self._should_close.set()
        if self.connection.state not in {
            wsproto.connection.ConnectionState.LOCAL_CLOSING,
            wsproto.connection.ConnectionState.CLOSED,
        }:
            event = wsproto.events.CloseConnection(code, reason)
            data = self.connection.send(event)
            with contextlib.suppress(httpcore.WriteError):
                await self.stream.write(data)

        await self.stream.aclose()

    async def _background_receive(self, max_bytes: int) -> None:
        """
        Background task listening for data from the server.

        Internally, it'll:

        * Answer to Ping events.
        * Acknowledge Pong events.
        * Put other events in the [_events][_events]
        queue that'll eventually be consumed by the user.

        Args:
            max_bytes: The maximum chunk size to read at each iteration.
        """
        try:
            while not self._should_close.is_set():
                data = await self._wait_until_closed(self.stream.read(max_bytes=max_bytes))
                self.connection.receive_data(data)
                for event in self.connection.events():
                    if isinstance(event, wsproto.events.Ping):
                        data = self.connection.send(event.response())
                        await self.stream.write(data)
                        continue
                    if isinstance(event, wsproto.events.Pong):
                        self._ping_manager.ack(event.payload)
                        continue
                    if isinstance(event, wsproto.events.CloseConnection):
                        self._should_close.set()
                    await self._events.put(event)
        except (httpcore.ReadError, httpcore.WriteError):
            await self.close(CloseReason.INTERNAL_ERROR, 'Stream error')
            await self._events.put(WebSocketNetworkError())
        except ShouldClose:
            pass

    async def _background_keepalive_ping(
        self, interval_seconds: float, timeout_seconds: typing.Optional[float] = None
    ) -> None:
        try:
            while not self._should_close.is_set():
                await self._wait_until_closed(asyncio.sleep(interval_seconds))
                pong_callback = await self.ping()
                if timeout_seconds is not None:
                    try:
                        await self._wait_until_closed(asyncio.wait_for(pong_callback.wait(), timeout_seconds))
                    except asyncio.TimeoutError:
                        await self.close(CloseReason.INTERNAL_ERROR, 'Keepalive ping timeout')
                        await self._events.put(WebSocketNetworkError())
        except ShouldClose:
            pass

    async def _wait_until_closed(self, coro: typing.Coroutine[typing.Any, typing.Any, TaskResult]) -> TaskResult:
        wait_close_task = asyncio.create_task(self._should_close.wait())
        todo_task = asyncio.create_task(coro)
        done, pending = await asyncio.wait({todo_task, wait_close_task}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        if wait_close_task in done and todo_task not in done:
            raise ShouldClose
        return todo_task.result()


def _get_headers(
    subprotocols: typing.Optional[typing.List[str]],
) -> typing.Dict[str, typing.Any]:
    headers = {
        'connection': 'upgrade',
        'upgrade': 'websocket',
        'sec-websocket-key': base64.b64encode(secrets.token_bytes(16)).decode('utf-8'),
        'sec-websocket-version': '13',
    }
    if subprotocols is not None:
        headers['sec-websocket-protocol'] = ', '.join(subprotocols)
    return headers


@contextlib.contextmanager
def _connect_ws(
    url: str,
    client: httpx.Client,
    *,
    max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
    keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
    subprotocols: typing.Optional[typing.List[str]] = None,
    **kwargs: typing.Any,
) -> typing.Generator[WebSocketSession, None, None]:
    headers = kwargs.pop('headers', {})
    headers.update(_get_headers(subprotocols))

    with client.stream('GET', url, headers=headers, **kwargs) as response:
        if response.status_code != 101:
            raise WebSocketUpgradeError(response)

        subprotocol = response.headers.get('sec-websocket-protocol')

        session = WebSocketSession(
            response.extensions['network_stream'],
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocol=subprotocol,
        )
        yield session
        session.close()


@contextlib.contextmanager
def connect_ws(
    url: str,
    client: typing.Optional[httpx.Client] = None,
    *,
    max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
    keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
    subprotocols: typing.Optional[typing.List[str]] = None,
    **kwargs: typing.Any,
) -> typing.Generator[WebSocketSession, None, None]:
    """
    Start a sync WebSocket session.

    It returns a context manager that'll automatically
    call [close()][ws_client.WebSocketSession.close] when exiting.

    Args:
        url: The WebSocket URL.
        client:
            HTTPX client to use.
            If not provided, a default one will be initialized.
        max_message_size_bytes:
            Message size in bytes to receive from the server.
            Defaults to 65 KiB.
        queue_size:
            Size of the queue where the received messages will be held
            until they are consumed.
            If the queue is full, the client will stop receive messages
            from the server until the queue has room available.
            Defaults to 512.
        keepalive_ping_interval_seconds:
            Interval at which the client will automatically send a Ping event
            to keep the connection alive. Set it to `None` to disable this mechanism.
            Defaults to 20 seconds.
        keepalive_ping_timeout_seconds:
            Maximum delay the client will wait for an answer to its Ping event.
            If the delay is exceeded,
            [WebSocketNetworkError][ws_client.WebSocketNetworkError]
            will be raised and the connection closed.
            Defaults to 20 seconds.
        subprotocols:
            Optional list of suprotocols to negotiate with the server.
        **kwargs:
            Additional keyword arguments that will be passed to
            the [HTTPX stream()](https://www.python-httpx.org/api/#request) method.

    Returns:
        A [context manager][contextlib.AbstractContextManager]
            for [WebSocketSession][ws_client.WebSocketSession].

    Examples:
        Without explicit HTTPX client.

            with connect_ws("http://localhost:8000/ws") as ws:
                message = ws.receive_text()
                print(message)
                ws.send_text("Hello!")

        With explicit HTTPX client.

            with httpx.Client() as client:
                with connect_ws("http://localhost:8000/ws", client) as ws:
                    message = ws.receive_text()
                    print(message)
                    ws.send_text("Hello!")
    """
    if client is None:
        with httpx.Client() as client, _connect_ws(
            url,
            client=client,
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocols=subprotocols,
            **kwargs,
        ) as websocket:
            yield websocket
    else:
        with _connect_ws(
            url,
            client=client,
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocols=subprotocols,
            **kwargs,
        ) as websocket:
            yield websocket


@contextlib.asynccontextmanager
async def _aconnect_ws(
    url: str,
    client: httpx.AsyncClient,
    *,
    max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
    keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
    subprotocols: typing.Optional[typing.List[str]] = None,
    **kwargs: typing.Any,
) -> typing.AsyncGenerator[AsyncWebSocketSession, None]:
    headers = kwargs.pop('headers', {})
    headers.update(_get_headers(subprotocols))

    async with client.stream('GET', url, headers=headers, **kwargs) as response:
        if response.status_code != 101:
            raise WebSocketUpgradeError(response)

        subprotocol = response.headers.get('sec-websocket-protocol')

        session = AsyncWebSocketSession(
            response.extensions['network_stream'],
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocol=subprotocol,
        )
        yield session
        await session.close()


@contextlib.asynccontextmanager
async def aconnect_ws(
    url: str,
    client: typing.Optional[httpx.AsyncClient] = None,
    *,
    max_message_size_bytes: int = DEFAULT_MAX_MESSAGE_SIZE_BYTES,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    keepalive_ping_interval_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_INTERVAL_SECONDS,
    keepalive_ping_timeout_seconds: typing.Optional[float] = DEFAULT_KEEPALIVE_PING_TIMEOUT_SECONDS,
    subprotocols: typing.Optional[typing.List[str]] = None,
    **kwargs: typing.Any,
) -> typing.AsyncGenerator[AsyncWebSocketSession, None]:
    """
    Start an async WebSocket session.

    It returns an async context manager that'll automatically
    call [close()][ws_client.AsyncWebSocketSession.close] when exiting.

    Args:
        url: The WebSocket URL.
        client:
            HTTPX client to use.
            If not provided, a default one will be initialized.
        max_message_size_bytes:
            Message size in bytes to receive from the server.
            Defaults to 65 KiB.
        queue_size:
            Size of the queue where the received messages will be held
            until they are consumed.
            If the queue is full, the client will stop receive messages
            from the server until the queue has room available.
            Defaults to 512.
        keepalive_ping_interval_seconds:
            Interval at which the client will automatically send a Ping event
            to keep the connection alive. Set it to `None` to disable this mechanism.
            Defaults to 20 seconds.
        keepalive_ping_timeout_seconds:
            Maximum delay the client will wait for an answer to its Ping event.
            If the delay is exceeded,
            [WebSocketNetworkError][ws_client.WebSocketNetworkError]
            will be raised and the connection closed.
            Defaults to 20 seconds.
        subprotocols:
            Optional list of suprotocols to negotiate with the server.
        **kwargs:
            Additional keyword arguments that will be passed to
            the [HTTPX stream()](https://www.python-httpx.org/api/#request) method.

    Returns:
        An [async context manager][contextlib.AbstractAsyncContextManager]
            for [AsyncWebSocketSession][ws_client.AsyncWebSocketSession].

    Examples:
        Without explicit HTTPX client.

            async with aconnect_ws("http://localhost:8000/ws") as ws:
                message = await ws.receive_text()
                print(message)
                await ws.send_text("Hello!")

        With explicit HTTPX client.

            async with httpx.AsyncClient() as client:
                async with aconnect_ws("http://localhost:8000/ws", client) as ws:
                    message = await ws.receive_text()
                    print(message)
                    await ws.send_text("Hello!")
    """
    if client is None:
        async with httpx.AsyncClient() as client, _aconnect_ws(
            url,
            client=client,
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocols=subprotocols,
            **kwargs,
        ) as websocket:
            yield websocket
    else:
        async with _aconnect_ws(
            url,
            client=client,
            max_message_size_bytes=max_message_size_bytes,
            queue_size=queue_size,
            keepalive_ping_interval_seconds=keepalive_ping_interval_seconds,
            keepalive_ping_timeout_seconds=keepalive_ping_timeout_seconds,
            subprotocols=subprotocols,
            **kwargs,
        ) as websocket:
            yield websocket
