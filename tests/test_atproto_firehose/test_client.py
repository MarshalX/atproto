"""Behavior of the Firehose clients against a real local WebSocket server.

These tests exist to pin down the contract the SDK relies on from the ``websockets`` library:
framing, reconnection, and which errors are fatal versus recoverable.
"""

import asyncio
import contextlib
import errno
import socket
import ssl
import threading
import time
import typing as t

import libipld
import pytest
from atproto_firehose import client as client_module
from atproto_firehose.client import (
    _AsyncWebsocketClient,
    _handle_websocket_error_or_stop,
    _WebsocketClient,
)
from atproto_firehose.exceptions import FirehoseError
from atproto_firehose.models import MessageFrame
from websockets.asyncio.client import connect

from .conftest import MAX_SIZE_BYTES, FirehoseTestServer

#: Generous upper bound; every scenario finishes in well under a second locally.
_TEST_TIMEOUT_SEC = 60

#: Reconnection uses exponential backoff in production. Tests replace it with a short delay.
_TEST_RECONNECT_DELAY_SEC = 0.05


class Outcome(t.NamedTuple):
    frames: t.List[MessageFrame]
    exception: t.Optional[BaseException]


def _shrink_backoff(client: t.Any) -> None:
    client._get_reconnection_delay = lambda: _TEST_RECONNECT_DELAY_SEC


def run_sync(
    server: FirehoseTestServer,
    method: str,
    params: t.Optional[dict] = None,
    recv_timeout: t.Optional[float] = None,
    stop_after: int = 1,
    configure: t.Optional[t.Callable[[t.Any], None]] = None,
) -> Outcome:
    """Run the sync client until ``stop_after`` frames arrive or it stops on its own."""
    client = _WebsocketClient(method, server.base_uri, params, recv_timeout=recv_timeout)
    _shrink_backoff(client)
    if configure is not None:
        configure(client)

    frames: t.List[MessageFrame] = []
    raised: t.List[BaseException] = []

    def on_message(frame: MessageFrame) -> None:
        frames.append(frame)
        if len(frames) >= stop_after:
            client.stop()

    def target() -> None:
        try:
            client.start(on_message)
        except BaseException as e:  # noqa: BLE001
            raised.append(e)

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(_TEST_TIMEOUT_SEC)
    client.stop()
    if thread.is_alive():
        raised.append(TimeoutError(f'the client did not stop within {_TEST_TIMEOUT_SEC}s'))

    return Outcome(frames, raised[0] if raised else None)


async def run_async(
    server: FirehoseTestServer,
    method: str,
    params: t.Optional[dict] = None,
    recv_timeout: t.Optional[float] = None,
    stop_after: int = 1,
    configure: t.Optional[t.Callable[[t.Any], None]] = None,
) -> Outcome:
    """Run the async client until ``stop_after`` frames arrive or it stops on its own."""
    client = _AsyncWebsocketClient(method, server.base_uri, params, recv_timeout=recv_timeout)
    _shrink_backoff(client)
    if configure is not None:
        configure(client)

    frames: t.List[MessageFrame] = []
    raised: t.List[BaseException] = []

    async def on_message(frame: MessageFrame) -> None:
        frames.append(frame)
        if len(frames) >= stop_after:
            await client.stop()

    task = asyncio.ensure_future(client.start(on_message))
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=_TEST_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        raised.append(TimeoutError(f'the client did not stop within {_TEST_TIMEOUT_SEC}s'))
    except BaseException as e:  # noqa: BLE001
        raised.append(e)
    finally:
        await client.stop()
        if not task.done():
            task.cancel()
        # the outcome was already captured above; a second raise here would mask it
        with contextlib.suppress(BaseException):
            await task

    return Outcome(frames, raised[0] if raised else None)


#: Runs the same assertions against both clients. The async runner is awaited by the caller.
RUNNERS = [run_sync, run_async]


async def _run(runner: t.Any, *args: t.Any, **kwargs: t.Any) -> Outcome:
    result = runner(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_receives_message_frames(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('three_messages_then_close')
    outcome = await _run(runner, server, method, stop_after=3)

    assert outcome.exception is None
    assert len(outcome.frames) == 3
    assert outcome.frames[0].type == '#commit'
    assert outcome.frames[0].body['repo'] == 'did:plc:test'
    assert [f.body['seq'] for f in outcome.frames] == [0, 1, 2]


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_error_frame_raises_firehose_error(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('error_frame')
    outcome = await _run(runner, server, method)

    assert isinstance(outcome.exception, FirehoseError)
    assert outcome.exception.args[0].error == 'ConsumerTooSlow'


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_clean_close_stops_without_error(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('one_message_then_clean_close')
    # never reached, so the client can only stop because the server closed normally
    outcome = await _run(runner, server, method, stop_after=1000)

    assert outcome.exception is None
    assert len(outcome.frames) == 1
    assert server.state(method).connections == 1  # a normal closure must not trigger a reconnect


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_reconnects_after_abnormal_close(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('abnormal_close')
    outcome = await _run(runner, server, method, stop_after=2)

    assert outcome.exception is None
    assert len(outcome.frames) == 2
    assert server.state(method).connections == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_reconnects_after_tcp_reset(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('tcp_reset')
    outcome = await _run(runner, server, method, stop_after=2)

    assert outcome.exception is None
    assert len(outcome.frames) == 2
    assert server.state(method).connections == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_skips_undecodable_frame(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('garbage_between_messages')
    outcome = await _run(runner, server, method, stop_after=2)

    assert outcome.exception is None
    assert [f.body['seq'] for f in outcome.frames] == [0, 1]
    assert server.state(method).connections == 1  # a bad frame must not drop the connection


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_skips_text_frames(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('text_then_message')
    outcome = await _run(runner, server, method)

    assert outcome.exception is None
    assert len(outcome.frames) == 1
    assert server.state(method).connections == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_recovers_from_oversized_frame(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('oversized_then_normal')
    outcome = await _run(runner, server, method)

    assert outcome.exception is None
    assert len(outcome.frames) == 1
    assert server.state(method).connections == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_accepts_message_below_size_limit(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('large_message')
    outcome = await _run(runner, server, method)

    assert outcome.exception is None
    assert len(outcome.frames[0].body['blob']) == 4 * 1024 * 1024


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_reassembles_fragmented_message(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('fragmented_message')
    outcome = await _run(runner, server, method)

    assert outcome.exception is None
    assert len(outcome.frames[0].body['blob']) == 1024 * 1024


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_recv_timeout_reconnects(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('silent_then_normal')
    outcome = await _run(runner, server, method, recv_timeout=0.4)

    assert outcome.exception is None
    assert outcome.frames[0].body['seq'] == 42
    assert server.state(method).connections == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_params_are_resent_on_reconnect(runner: t.Any, server: FirehoseTestServer) -> None:
    method = server.new_method('abnormal_close')
    outcome = await _run(runner, server, method, params={'cursor': 123}, stop_after=2)

    assert outcome.exception is None
    assert [q.get('cursor') for q in server.state(method).queries] == ['123', '123']


@pytest.mark.asyncio
async def test_updated_params_are_used_on_reconnect(server: FirehoseTestServer) -> None:
    """``update_params`` must take effect on the next connection, not the current one."""
    method = server.new_method('abnormal_close')
    client = _AsyncWebsocketClient(method, server.base_uri, {'cursor': 1})
    _shrink_backoff(client)

    frames: t.List[MessageFrame] = []

    async def on_message(frame: MessageFrame) -> None:
        frames.append(frame)
        client.update_params({'cursor': 2})
        if len(frames) >= 2:
            await client.stop()

    await asyncio.wait_for(client.start(on_message), timeout=_TEST_TIMEOUT_SEC)

    assert [q.get('cursor') for q in server.state(method).queries] == ['1', '2']


@pytest.mark.asyncio
async def test_recv_cancellation_does_not_lose_messages(server: FirehoseTestServer) -> None:
    """The async client wraps ``recv()`` in ``asyncio.wait_for``.

    That is only safe because ``websockets`` guarantees cancelling ``recv()`` loses no data.
    """
    method = server.new_method('delayed_send')
    async with connect(f'{server.base_uri}/{method}', max_size=MAX_SIZE_BYTES) as ws:
        for _ in range(3):
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(ws.recv(), timeout=0.05)

        data = await asyncio.wait_for(ws.recv(), timeout=_TEST_TIMEOUT_SEC)

    assert isinstance(data, bytes)
    assert libipld.decode_dag_cbor_multi(data)[1]['seq'] == 42


#: Errors a long-running consumer is expected to survive. Each of these used to be fatal.
TRANSIENT_ERRORS = [
    pytest.param(OSError(errno.ENETUNREACH, 'Network is unreachable'), id='enetunreach'),
    pytest.param(OSError(errno.EHOSTUNREACH, 'No route to host'), id='ehostunreach'),
    pytest.param(ssl.SSLError('handshake failure'), id='ssl-error'),
    pytest.param(ssl.SSLEOFError('EOF'), id='ssl-eof'),
    pytest.param(socket.herror('host error'), id='herror'),
    pytest.param(socket.gaierror('name resolution'), id='gaierror'),
    pytest.param(ConnectionResetError(), id='connection-reset'),
    pytest.param(TimeoutError(), id='timeout'),
    pytest.param(asyncio.TimeoutError(), id='asyncio-timeout'),
]


@pytest.mark.parametrize('exception', TRANSIENT_ERRORS)
def test_transient_network_errors_are_recoverable(exception: Exception) -> None:
    """A dropped network must reconnect the client, not stop it."""
    assert _handle_websocket_error_or_stop(exception) is False


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_reconnects_when_network_is_unreachable(runner: t.Any, server: FirehoseTestServer) -> None:
    """The first connect attempt fails the way a sleeping laptop fails."""
    method = server.new_method('text_then_message')

    def configure(client: t.Any) -> None:
        attempts = []

        def fail_once(original: t.Callable[[], t.Any]) -> t.Callable[[], t.Any]:
            def factory() -> t.Any:
                attempts.append(1)
                if len(attempts) == 1:
                    raise OSError(errno.ENETUNREACH, 'Network is unreachable')
                return original()

            return factory

        client._get_client = fail_once(client._get_client)
        client._get_async_client = fail_once(client._get_async_client)

    outcome = await _run(runner, server, method, configure=configure)

    assert outcome.exception is None
    assert len(outcome.frames) == 1


def test_unexpected_exception_keeps_its_message() -> None:
    """An unrecognised error must not surface as a blank FirehoseError."""
    cause = ValueError('something specific went wrong')

    with pytest.raises(FirehoseError) as exc_info:
        _handle_websocket_error_or_stop(cause)

    assert 'something specific went wrong' in str(exc_info.value)
    assert exc_info.value.__cause__ is cause


def _record_backoff(client: t.Any, attempts: t.List[int]) -> None:
    """Capture the reconnect counter at each delay, without actually sleeping."""

    def delay() -> float:
        attempts.append(client._reconnect_no)
        return 0.01

    client._get_reconnection_delay = delay


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_backoff_escalates_against_a_flapping_server(runner: t.Any, server: FirehoseTestServer) -> None:
    """A server that accepts then immediately drops must not be hammered at a fixed rate."""
    method = server.new_method('always_drops')
    attempts: t.List[int] = []

    outcome = await _run(runner, server, method, stop_after=4, configure=lambda c: _record_backoff(c, attempts))

    assert outcome.exception is None
    assert attempts[:3] == [1, 2, 3]


@pytest.mark.asyncio
@pytest.mark.parametrize('runner', RUNNERS)
async def test_backoff_resets_after_a_healthy_connection(
    runner: t.Any, server: FirehoseTestServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A long-lived connection dropping is a one-off, not evidence of a failing server."""
    monkeypatch.setattr(client_module, '_HEALTHY_CONNECTION_SEC', 0.0)
    method = server.new_method('always_drops')
    attempts: t.List[int] = []

    outcome = await _run(runner, server, method, stop_after=4, configure=lambda c: _record_backoff(c, attempts))

    assert outcome.exception is None
    assert attempts[:3] == [1, 1, 1]


def _wait_for_connection(server: FirehoseTestServer, method: str) -> None:
    deadline = time.monotonic() + _TEST_TIMEOUT_SEC
    while time.monotonic() < deadline:
        if server.state(method).connections:
            time.sleep(0.1)  # let the client settle into recv()
            return
        time.sleep(0.02)
    raise AssertionError('the client never connected')


def test_sync_stop_interrupts_an_idle_connection(server: FirehoseTestServer) -> None:
    """``stop()`` from another thread must not wait for a frame that may never arrive."""
    method = server.new_method('idle')
    client = _WebsocketClient(method, server.base_uri)
    _shrink_backoff(client)
    finished = threading.Event()

    def target() -> None:
        client.start(lambda _: None)
        finished.set()

    threading.Thread(target=target, daemon=True).start()
    _wait_for_connection(server, method)

    client.stop()

    assert finished.wait(5), 'start() did not return after stop()'


@pytest.mark.asyncio
async def test_async_stop_interrupts_an_idle_connection(server: FirehoseTestServer) -> None:
    """``stop()`` from another task must not wait for a frame that may never arrive."""
    method = server.new_method('idle')
    client = _AsyncWebsocketClient(method, server.base_uri)
    _shrink_backoff(client)

    async def on_message(_: MessageFrame) -> None:
        return None

    task = asyncio.ensure_future(client.start(on_message))
    await asyncio.get_running_loop().run_in_executor(None, _wait_for_connection, server, method)

    await client.stop()

    await asyncio.wait_for(task, timeout=5)


def test_sync_client_enables_keepalive(server: FirehoseTestServer) -> None:
    """Without pings, a connection that is open but no longer delivering is undetectable."""
    client = _WebsocketClient(server.new_method('idle'), server.base_uri)

    with client._get_client() as connection:
        assert connection.ping_interval is not None
