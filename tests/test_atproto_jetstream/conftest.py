"""A local WebSocket server that speaks the Jetstream v2 `xrpc.v1.json` framing.

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

import pytest
import websockets
from pydantic_core import to_json
from websockets.asyncio.server import serve
from websockets.typing import Subprotocol

SUBPROTOCOL = Subprotocol('xrpc.v1.json')

_SERVER_START_TIMEOUT_SEC = 30

#: Long enough that the client always acts first; the connection is torn down with the test.
_IDLE_SEC = 30


def commit_frame(seq: int, text: str = 'hello') -> str:
    """Build a Jetstream `#commit` message frame."""
    return message_frame(
        {
            '$type': 'network.bsky.jetstream.subscribeEvents#commit',
            'seq': seq,
            'did': 'did:plc:test',
            'time': '2026-08-17T12:00:00.000000Z',
            'rev': '3l3qo2vutsw2b',
            'operation': 'create',
            'collection': 'app.bsky.feed.post',
            'rkey': '3l3qo2vuowo2b',
            'cid': 'bafyreidwaivazkwu67xztlmuobx35hs2lnfh3kolmgfmucldvhd3sgzcqi',
            'record': {'$type': 'app.bsky.feed.post', 'text': text, 'createdAt': '2026-08-17T12:00:00.000Z'},
        }
    )


def info_frame(name: str = 'OutdatedCursor') -> str:
    """Build a Jetstream `#info` message frame. It carries no seq."""
    return message_frame({'$type': 'network.bsky.jetstream.subscribeEvents#info', 'name': name, 'message': 'clamped'})


def message_frame(payload: dict) -> str:
    return to_json({'$type': 'message', 'payload': payload}).decode('UTF-8')


def error_frame(error: str, message: str) -> str:
    """Build a Jetstream error frame."""
    return to_json({'$type': 'error', 'error': error, 'message': message}).decode('UTF-8')


#: Not valid JSON; the client must skip it instead of dropping the connection.
GARBAGE_FRAME = '{not json'


class _State:
    """Per-scenario-instance server state."""

    def __init__(self) -> None:
        self.connections = 0
        self.rejections = 0
        self.queries: t.List[t.Dict[str, t.List[str]]] = []
        self.subprotocols: t.List[t.Optional[str]] = []


class JetstreamTestServer:
    """A WebSocket server dispatching to a scenario handler based on the request path."""

    def __init__(self) -> None:
        self._port: t.Optional[int] = None
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._states: t.Dict[str, _State] = {}

    def start(self) -> None:
        threading.Thread(target=self._run, daemon=True).start()
        if not self._ready.wait(_SERVER_START_TIMEOUT_SEC):
            raise RuntimeError('the test WebSocket server did not start in time')

    def _process_request(self, connection: t.Any, request: t.Any) -> t.Any:
        """Reject the handshake before the upgrade, the way the real server rejects a stale cursor."""
        method = urlparse(request.path).path.rsplit('/', 1)[-1]
        rejection = PRE_UPGRADE_REJECTIONS.get(method.split('.', 1)[0])
        if rejection is None:
            return None

        state = self.state(method)
        status_code, body, only_once = rejection
        with self._lock:
            if only_once and state.rejections:
                return None

            state.rejections += 1

        return connection.respond(status_code, body)

    def _run(self) -> None:
        async def main() -> None:
            async with await serve(
                self._handle,
                '127.0.0.1',
                0,
                subprotocols=[SUBPROTOCOL],
                process_request=self._process_request,
            ) as server:
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
            state.queries.append(parse_qs(parsed.query))
            state.subprotocols.append(websocket.subprotocol)

        # the client disconnects on its own in most scenarios; that is not a server error
        with contextlib.suppress(websockets.exceptions.ConnectionClosed):
            await SCENARIOS[scenario](websocket, connection_no)


async def _three_commits_then_close(ws: t.Any, connection_no: int) -> None:
    for seq in range(1, 4):
        await ws.send(commit_frame(seq))
    await ws.close(1000)


async def _info_then_commit(ws: t.Any, connection_no: int) -> None:
    await ws.send(info_frame())
    await ws.send(commit_frame(7))
    await asyncio.sleep(_IDLE_SEC)


async def _garbage_between_commits(ws: t.Any, connection_no: int) -> None:
    await ws.send(commit_frame(1))
    await ws.send(GARBAGE_FRAME)
    await ws.send(message_frame({'$type': 'network.bsky.jetstream.subscribeEvents#somethingNew', 'seq': 2}))
    await ws.send(to_json({'$type': 'somethingElse'}).decode('UTF-8'))
    await ws.send(commit_frame(3))
    await asyncio.sleep(_IDLE_SEC)


async def _consumer_too_slow_then_commit(ws: t.Any, connection_no: int) -> None:
    if connection_no == 1:
        await ws.send(error_frame('ConsumerTooSlow', 'you are too slow'))
        await asyncio.sleep(_IDLE_SEC)
    else:
        await ws.send(commit_frame(5))
        await asyncio.sleep(_IDLE_SEC)


async def _fatal_error_frame(ws: t.Any, connection_no: int) -> None:
    await ws.send(error_frame('SomethingFatal', 'game over'))
    await asyncio.sleep(_IDLE_SEC)


async def _redelivers_on_reconnect(ws: t.Any, connection_no: int) -> None:
    """Replays inclusively from the cursor, exactly as the real server does."""
    if connection_no == 1:
        await ws.send(commit_frame(10))
        await ws.send(commit_frame(11))
        await ws.close(1011, 'boom')
    else:
        # the client must have asked for cursor=11; replay it and continue
        await ws.send(commit_frame(11))
        await ws.send(commit_frame(12))
        await asyncio.sleep(_IDLE_SEC)


async def _silent_then_commit(ws: t.Any, connection_no: int) -> None:
    if connection_no == 1:
        await asyncio.sleep(_IDLE_SEC)  # the client must hit recv_timeout and reconnect
    else:
        await ws.send(commit_frame(42))
        await asyncio.sleep(_IDLE_SEC)


async def _commit_once(ws: t.Any, connection_no: int) -> None:
    await ws.send(commit_frame(42))
    await asyncio.sleep(_IDLE_SEC)


#: Scenarios rejected before the websocket upgrade: HTTP status, body, and whether only the first attempt is rejected.
PRE_UPGRADE_REJECTIONS: t.Dict[str, t.Tuple[int, str, bool]] = {
    'cursor_too_old': (400, '{"error":"CursorTooOld","message":"cursor 1 below lookback floor"}', False),
    'invalid_request': (400, '{"error":"InvalidRequest","message":"unknown kind"}', False),
    'server_error_then_ok': (503, 'try again later', True),
}

SCENARIOS: t.Dict[str, t.Callable[[t.Any, int], t.Coroutine[t.Any, t.Any, None]]] = {
    'three_commits_then_close': _three_commits_then_close,
    'info_then_commit': _info_then_commit,
    'garbage_between_commits': _garbage_between_commits,
    'consumer_too_slow_then_commit': _consumer_too_slow_then_commit,
    'fatal_error_frame': _fatal_error_frame,
    'redelivers_on_reconnect': _redelivers_on_reconnect,
    'silent_then_commit': _silent_then_commit,
    'server_error_then_ok': _commit_once,
}


@pytest.fixture(scope='session')
def server() -> JetstreamTestServer:
    instance = JetstreamTestServer()
    instance.start()
    return instance
