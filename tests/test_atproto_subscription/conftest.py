"""A local WebSocket server that speaks the atproto Firehose framing.

Nothing here touches the network.

Each test gets its own scenario instance (``<scenario>.<uuid>`` as the XRPC method) so that
handlers can branch on the connection number without leaking state between tests.
"""

import asyncio
import contextlib
import threading
import typing as t
import uuid
from urllib.parse import parse_qs, urlparse

import libipld
import pytest
import websockets
from websockets.asyncio.server import serve

MAX_SIZE_BYTES = 1024 * 1024 * 5  # mirrors _MAX_MESSAGE_SIZE_BYTES in the client

_SERVER_START_TIMEOUT_SEC = 30


def message_frame(seq: int, payload_size: int = 0) -> bytes:
    """Build a Firehose message frame: DAG-CBOR header followed by DAG-CBOR body."""
    header = libipld.encode_dag_cbor({'op': 1, 't': '#commit'})
    body = {'seq': seq, 'repo': 'did:plc:test', 'blob': b'x' * payload_size}
    return header + libipld.encode_dag_cbor(body)


def error_frame(error: str, message: str) -> bytes:
    """Build a Firehose error frame."""
    header = libipld.encode_dag_cbor({'op': -1})
    return header + libipld.encode_dag_cbor({'error': error, 'message': message})


#: Not valid DAG-CBOR; the client must skip it instead of dropping the connection.
GARBAGE_FRAME = b'\xff\xff\xff\xff\xff'


class _State:
    """Per-scenario-instance server state."""

    def __init__(self) -> None:
        self.connections = 0
        self.queries: t.List[t.Dict[str, str]] = []


class FirehoseTestServer:
    """A WebSocket server dispatching to a scenario handler based on the request path."""

    def __init__(self) -> None:
        self._port: t.Optional[int] = None
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._states: t.Dict[str, _State] = {}
        self._loop: t.Optional[asyncio.AbstractEventLoop] = None

    def start(self) -> None:
        threading.Thread(target=self._run, daemon=True).start()
        if not self._ready.wait(_SERVER_START_TIMEOUT_SEC):
            raise RuntimeError('the test WebSocket server did not start in time')

    def _run(self) -> None:
        async def main() -> None:
            self._loop = asyncio.get_running_loop()
            # max_size=None so the server may send frames larger than the client accepts
            async with await serve(self._handle, '127.0.0.1', 0, max_size=None) as server:
                self._port = next(iter(server.sockets)).getsockname()[1]
                self._ready.set()
                await asyncio.get_running_loop().create_future()  # serve until the thread dies

        asyncio.run(main())

    @property
    def base_uri(self) -> str:
        return f'ws://127.0.0.1:{self._port}/xrpc'

    def state(self, method: str) -> _State:
        with self._lock:
            return self._states.setdefault(method, _State())

    def new_method(self, scenario: str) -> str:
        """Return a unique XRPC method routing to ``scenario``, isolated from other tests."""
        return f'{scenario}.{uuid.uuid4().hex}'

    async def _handle(self, websocket: t.Any) -> None:
        parsed = urlparse(websocket.request.path)
        method = parsed.path.rsplit('/', 1)[-1]
        scenario = method.split('.', 1)[0]

        state = self.state(method)
        with self._lock:
            state.connections += 1
            connection_no = state.connections
            state.queries.append({k: v[0] for k, v in parse_qs(parsed.query).items()})

        # the client disconnects on its own in most scenarios; that is not a server error
        with contextlib.suppress(websockets.exceptions.ConnectionClosed):
            await SCENARIOS[scenario](websocket, connection_no)


#: Long enough that the client always acts first; the connection is torn down with the test.
_IDLE_SEC = 30


async def _three_messages_then_close(ws: t.Any, connection_no: int) -> None:
    for seq in range(3):
        await ws.send(message_frame(seq))
    await ws.close(1000)


async def _error_frame(ws: t.Any, connection_no: int) -> None:
    await ws.send(error_frame('ConsumerTooSlow', 'you are too slow'))
    await asyncio.sleep(_IDLE_SEC)


async def _one_message_then_clean_close(ws: t.Any, connection_no: int) -> None:
    await ws.send(message_frame(0))
    await ws.close(1000)


async def _abnormal_close(ws: t.Any, connection_no: int) -> None:
    await ws.send(message_frame(connection_no))
    if connection_no == 1:
        await ws.close(1011, 'boom')
    else:
        await asyncio.sleep(_IDLE_SEC)


async def _tcp_reset(ws: t.Any, connection_no: int) -> None:
    await ws.send(message_frame(connection_no))
    if connection_no == 1:
        await asyncio.sleep(0.05)  # let the frame reach the client before the reset
        ws.transport.abort()  # hard reset, no closing handshake
    else:
        await asyncio.sleep(_IDLE_SEC)


async def _garbage_between_messages(ws: t.Any, connection_no: int) -> None:
    await ws.send(message_frame(0))
    await ws.send(GARBAGE_FRAME)
    await ws.send(message_frame(1))
    await asyncio.sleep(_IDLE_SEC)


async def _text_then_message(ws: t.Any, connection_no: int) -> None:
    await ws.send('a text frame that the client must skip')
    await ws.send(message_frame(0))
    await asyncio.sleep(_IDLE_SEC)


async def _oversized_then_normal(ws: t.Any, connection_no: int) -> None:
    if connection_no == 1:
        await ws.send(b'x' * (MAX_SIZE_BYTES + 1024))
        await asyncio.sleep(_IDLE_SEC)
    else:
        await ws.send(message_frame(0))
        await asyncio.sleep(_IDLE_SEC)


async def _large_message(ws: t.Any, connection_no: int) -> None:
    await ws.send(message_frame(0, payload_size=4 * 1024 * 1024))
    await asyncio.sleep(_IDLE_SEC)


async def _fragmented_message(ws: t.Any, connection_no: int) -> None:
    data = message_frame(0, payload_size=1024 * 1024)
    chunk = 64 * 1024
    await ws.send(data[i : i + chunk] for i in range(0, len(data), chunk))
    await asyncio.sleep(_IDLE_SEC)


async def _silent_then_normal(ws: t.Any, connection_no: int) -> None:
    if connection_no == 1:
        await asyncio.sleep(_IDLE_SEC)  # the client must hit recv_timeout and reconnect
    else:
        await ws.send(message_frame(42))
        await asyncio.sleep(_IDLE_SEC)


async def _delayed_send(ws: t.Any, connection_no: int) -> None:
    await asyncio.sleep(0.4)
    await ws.send(message_frame(42))
    await asyncio.sleep(_IDLE_SEC)


async def _always_drops(ws: t.Any, connection_no: int) -> None:
    """An overloaded server: accepts, delivers one frame, drops. Never settles."""
    await ws.send(message_frame(connection_no))
    await ws.close(1011, 'overloaded')


async def _idle(ws: t.Any, connection_no: int) -> None:
    """Holds the connection open and sends nothing, parking the client in recv()."""
    await asyncio.sleep(_IDLE_SEC)


SCENARIOS: t.Dict[str, t.Callable[[t.Any, int], t.Coroutine[t.Any, t.Any, None]]] = {
    'three_messages_then_close': _three_messages_then_close,
    'error_frame': _error_frame,
    'one_message_then_clean_close': _one_message_then_clean_close,
    'abnormal_close': _abnormal_close,
    'tcp_reset': _tcp_reset,
    'garbage_between_messages': _garbage_between_messages,
    'text_then_message': _text_then_message,
    'oversized_then_normal': _oversized_then_normal,
    'large_message': _large_message,
    'fragmented_message': _fragmented_message,
    'silent_then_normal': _silent_then_normal,
    'delayed_send': _delayed_send,
    'always_drops': _always_drops,
    'idle': _idle,
}


@pytest.fixture(scope='session')
def server() -> FirehoseTestServer:
    instance = FirehoseTestServer()
    instance.start()
    return instance
