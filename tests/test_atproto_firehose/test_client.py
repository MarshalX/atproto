"""Behavior of the Firehose clients against a real local WebSocket server.

These tests exist to pin down the contract the SDK relies on from the ``websockets`` library:
framing, reconnection, and which errors are fatal versus recoverable.
"""

import asyncio
import contextlib
import threading
import typing as t

import libipld
import pytest
from atproto_firehose.client import _AsyncWebsocketClient, _WebsocketClient
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
) -> Outcome:
    """Run the sync client until ``stop_after`` frames arrive or it stops on its own."""
    client = _WebsocketClient(method, server.base_uri, params, recv_timeout=recv_timeout)
    _shrink_backoff(client)

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
) -> Outcome:
    """Run the async client until ``stop_after`` frames arrive or it stops on its own."""
    client = _AsyncWebsocketClient(method, server.base_uri, params, recv_timeout=recv_timeout)
    _shrink_backoff(client)

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
