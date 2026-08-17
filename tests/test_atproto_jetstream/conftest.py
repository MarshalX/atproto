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
import zstandard
from pydantic_core import to_json
from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.http11 import Response
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

GET_ZSTD_DICTIONARY_PATH = '/xrpc/network.bsky.jetstream.getZstdDictionary'


def _train_dictionary(salt: str) -> zstandard.ZstdCompressionDict:
    """Build a dictionary. Distinct salts give distinct dictionary IDs, so rotation is testable."""
    samples = [commit_frame(i, text=f'{salt} sample {i}').encode('UTF-8') for i in range(400)]
    # the stub asks for ByteString, which is deprecated; bytes is what it actually accepts
    return zstandard.train_dictionary(4096, t.cast('t.Any', samples))


#: Two dictionaries so a scenario can rotate from one to the other.
DICTIONARIES = {'current': _train_dictionary('current'), 'rotated': _train_dictionary('rotated')}


def compress(frame: str, dictionary: zstandard.ZstdCompressionDict) -> bytes:
    return zstandard.ZstdCompressor(dict_data=dictionary).compress(frame.encode('UTF-8'))


class _State:
    """Per-scenario-instance server state."""

    def __init__(self) -> None:
        self.connections = 0
        self.rejections = 0
        self.queries: t.List[t.Dict[str, t.List[str]]] = []
        self.subprotocols: t.List[t.Optional[str]] = []
        self.dictionary_fetches = 0


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
        """Serve the dictionary over HTTP, or reject the handshake before the upgrade."""
        path = urlparse(request.path).path
        if path.endswith(GET_ZSTD_DICTIONARY_PATH.rsplit('/', 1)[-1]):
            return self._serve_dictionary(connection, path)

        method = path.rsplit('/', 1)[-1]
        rejection = PRE_UPGRADE_REJECTIONS.get(method.split('.', 1)[0])
        if rejection is None:
            return None

        state = self.state(method)
        status_code, body, only_once = rejection

        # a dictionary rejection only makes sense when the client actually offered one
        if 'UnknownZstdDictionary' in body and 'zstdDictionary' not in parse_qs(urlparse(request.path).query):
            return None

        with self._lock:
            if only_once and state.rejections:
                return None

            state.rejections += 1

        return connection.respond(status_code, body)

    def _serve_dictionary(self, connection: t.Any, path: str) -> t.Any:
        method = path.strip('/').split('/')[0]
        state = self.state(method)
        with self._lock:
            state.dictionary_fetches += 1

        if 'unavailable' in method:
            return connection.respond(500, 'no dictionary here')

        # respond() is text-only; the dictionary is binary
        body = self.dictionary_for(method).as_bytes()
        headers = Headers([('Content-Type', 'application/octet-stream'), ('Content-Length', str(len(body)))])

        return Response(200, 'OK', headers, body)

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

    def base_uri_for(self, method: str) -> str:
        """Base URI carrying the scenario token, so the dictionary endpoint can resolve state.

        The client derives the dictionary URL from this same base, which is how one server
        serves both the websocket and the HTTP dictionary fetch on one port.
        """
        return f'ws://127.0.0.1:{self._port}/{method}/xrpc'

    def dictionary_for(self, method: str) -> zstandard.ZstdCompressionDict:
        """Dictionary this scenario instance is currently serving."""
        state = self.state(method)
        return DICTIONARIES['rotated' if state.dictionary_fetches > 1 and 'rotate' in method else 'current']

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


async def _compressed_commits(ws: t.Any, connection_no: int) -> None:
    """Honour the client's choice: compressed frames when it negotiated a dictionary."""
    query = parse_qs(urlparse(ws.request.path).query)
    method = urlparse(ws.request.path).path.rsplit('/', 1)[-1]
    dictionary_id = query.get('zstdDictionary')

    for seq in range(1, 4):
        frame = commit_frame(seq)
        if dictionary_id:
            await ws.send(compress(frame, SERVER.dictionary_for(method)))
        else:
            await ws.send(frame)
    await asyncio.sleep(_IDLE_SEC)


async def _compressed_garbage(ws: t.Any, connection_no: int) -> None:
    """A frame that is not valid zstd, then a good one. The bad frame must be skipped."""
    method = urlparse(ws.request.path).path.rsplit('/', 1)[-1]
    dictionary = SERVER.dictionary_for(method)
    await ws.send(compress(commit_frame(1), dictionary))
    await ws.send(b'\x28\xb5\x2f\xfd not really a zstd frame')
    await ws.send(compress(commit_frame(3), dictionary))
    await asyncio.sleep(_IDLE_SEC)


async def _commit_once(ws: t.Any, connection_no: int) -> None:
    await ws.send(commit_frame(42))
    await asyncio.sleep(_IDLE_SEC)


#: Scenarios rejected before the websocket upgrade: HTTP status, body, and whether only the first attempt is rejected.
PRE_UPGRADE_REJECTIONS: t.Dict[str, t.Tuple[int, str, bool]] = {
    'cursor_too_old': (400, '{"error":"CursorTooOld","message":"cursor 1 below lookback floor"}', False),
    'invalid_request': (400, '{"error":"InvalidRequest","message":"unknown kind"}', False),
    'server_error_then_ok': (503, 'try again later', True),
    # the dictionary rotated: refuse once, then accept whatever the client refetched
    'dict_rotate': (400, '{"error":"UnknownZstdDictionary","message":"retrained"}', True),
    # a mixed-version fleet: always refuse, and keep handing back the same id
    'dict_stale': (400, '{"error":"UnknownZstdDictionary","message":"retired"}', False),
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
    'compressed': _compressed_commits,
    'compressed_garbage': _compressed_garbage,
    'dict_rotate': _compressed_commits,
    'dict_stale': _compressed_commits,
    'dict_unavailable': _compressed_commits,
}


#: The scenario handlers need the server to resolve which dictionary to compress with.
SERVER = JetstreamTestServer()


@pytest.fixture(scope='session')
def server() -> JetstreamTestServer:
    if SERVER._port is None:
        SERVER.start()

    return SERVER
