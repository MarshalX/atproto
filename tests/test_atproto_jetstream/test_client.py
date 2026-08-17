"""Behavior of the Jetstream v2 clients against a real local WebSocket server.

These tests pin down the v2 contract: `xrpc.v1.json` framing, cursor tracking with
deduplication, and which errors are fatal versus recoverable.
"""

import asyncio
import contextlib
import threading
import typing as t

import pytest
from atproto_client import models
from atproto_jetstream.client import _AsyncJetstreamClient, _JetstreamClient
from atproto_jetstream.exceptions import JetstreamCursorTooOldError, JetstreamError
from atproto_jetstream.jetstream import AsyncJetstreamClient, JetstreamClient
from atproto_jetstream.models import SubscribeEventsMessage

from .conftest import DICTIONARIES, SUBPROTOCOL, JetstreamTestServer

#: Generous upper bound; every scenario finishes in well under a second locally.
_TEST_TIMEOUT_SEC = 60

#: Reconnection uses exponential backoff in production. Tests replace it with a short delay.
_TEST_RECONNECT_DELAY_SEC = 0.05

Commit = models.NetworkBskyJetstreamSubscribeEvents.Commit
Info = models.NetworkBskyJetstreamSubscribeEvents.Info


class Outcome(t.NamedTuple):
    messages: t.List[SubscribeEventsMessage]
    exception: t.Optional[BaseException]
    cursor: t.Optional[int]
    compressed: bool = False


def seqs(outcome: 'Outcome') -> t.List[int]:
    """Seqs of the delivered events. Every kind except #info carries one."""
    return [message.seq for message in outcome.messages if not isinstance(message, Info)]


def first_commit(outcome: 'Outcome') -> Commit:
    assert isinstance(outcome.messages[0], Commit)
    return outcome.messages[0]


def _shrink_backoff(client: t.Any) -> None:
    client._get_reconnection_delay = lambda: _TEST_RECONNECT_DELAY_SEC


def run_sync(
    server: JetstreamTestServer,
    method: str,
    params: t.Optional[dict] = None,
    recv_timeout: t.Optional[float] = None,
    stop_after: int = 1,
    compress: bool = False,
) -> Outcome:
    """Run the sync client until ``stop_after`` messages arrive or it stops on its own."""
    client = _JetstreamClient(method, server.base_uri_for(method), params, recv_timeout=recv_timeout, compress=compress)
    _shrink_backoff(client)

    messages: t.List[SubscribeEventsMessage] = []
    raised: t.List[BaseException] = []

    def on_message(message: SubscribeEventsMessage) -> None:
        messages.append(message)
        if len(messages) >= stop_after:
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

    return Outcome(messages, raised[0] if raised else None, client.cursor, client.compressed)


async def run_async(
    server: JetstreamTestServer,
    method: str,
    params: t.Optional[dict] = None,
    recv_timeout: t.Optional[float] = None,
    stop_after: int = 1,
    compress: bool = False,
) -> Outcome:
    """Run the async client until ``stop_after`` messages arrive or it stops on its own."""
    client = _AsyncJetstreamClient(
        method, server.base_uri_for(method), params, recv_timeout=recv_timeout, compress=compress
    )
    _shrink_backoff(client)

    messages: t.List[SubscribeEventsMessage] = []
    raised: t.List[BaseException] = []

    async def on_message(message: SubscribeEventsMessage) -> None:
        messages.append(message)
        if len(messages) >= stop_after:
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

    return Outcome(messages, raised[0] if raised else None, client.cursor, client.compressed)


def test_delivers_parsed_commits(server: JetstreamTestServer) -> None:
    method = server.new_method('three_commits_then_close')

    outcome = run_sync(server, method, stop_after=3)

    assert outcome.exception is None
    assert seqs(outcome) == [1, 2, 3]
    assert all(isinstance(m, Commit) for m in outcome.messages)
    assert first_commit(outcome).collection == 'app.bsky.feed.post'


def test_record_is_typed(server: JetstreamTestServer) -> None:
    method = server.new_method('three_commits_then_close')

    outcome = run_sync(server, method, stop_after=1)

    post = models.get_or_create(first_commit(outcome).record, models.AppBskyFeedPost.Record)

    assert isinstance(post, models.AppBskyFeedPost.Record)
    assert post.text == 'hello'


def test_offers_the_xrpc_v1_json_subprotocol(server: JetstreamTestServer) -> None:
    method = server.new_method('three_commits_then_close')

    run_sync(server, method, stop_after=1)

    assert server.state(method).subprotocols == [SUBPROTOCOL]


def test_cursor_tracks_the_last_delivered_seq(server: JetstreamTestServer) -> None:
    method = server.new_method('three_commits_then_close')

    outcome = run_sync(server, method, stop_after=3)

    assert outcome.cursor == 3


def test_info_is_delivered_but_does_not_advance_the_cursor(server: JetstreamTestServer) -> None:
    method = server.new_method('info_then_commit')

    outcome = run_sync(server, method, stop_after=1)

    info = outcome.messages[0]
    assert isinstance(info, Info)
    assert info.name == 'OutdatedCursor'
    assert outcome.cursor is None


def test_undecodable_and_unknown_frames_are_skipped(server: JetstreamTestServer) -> None:
    method = server.new_method('garbage_between_commits')

    outcome = run_sync(server, method, stop_after=2)

    assert outcome.exception is None
    assert seqs(outcome) == [1, 3]


def test_from_tip_start_omits_the_cursor_until_the_first_event(server: JetstreamTestServer) -> None:
    method = server.new_method('redelivers_on_reconnect')

    run_sync(server, method, stop_after=3)

    queries = server.state(method).queries
    assert 'cursor' not in queries[0]


def test_reconnect_resumes_from_the_cursor_and_dedups(server: JetstreamTestServer) -> None:
    method = server.new_method('redelivers_on_reconnect')

    outcome = run_sync(server, method, stop_after=3)

    # seq 11 is replayed by the server after the drop and must not be delivered twice
    assert seqs(outcome) == [10, 11, 12]
    assert server.state(method).queries[1]['cursor'] == ['11']
    assert outcome.cursor == 12


def test_consumer_too_slow_reconnects(server: JetstreamTestServer) -> None:
    method = server.new_method('consumer_too_slow_then_commit')

    outcome = run_sync(server, method, stop_after=1)

    assert outcome.exception is None
    assert seqs(outcome) == [5]
    assert server.state(method).connections == 2


def test_unknown_error_frame_is_fatal(server: JetstreamTestServer) -> None:
    method = server.new_method('fatal_error_frame')

    outcome = run_sync(server, method, stop_after=1)

    assert isinstance(outcome.exception, JetstreamError)
    assert outcome.messages == []


def test_recv_timeout_reconnects(server: JetstreamTestServer) -> None:
    method = server.new_method('silent_then_commit')

    outcome = run_sync(server, method, recv_timeout=0.2, stop_after=1)

    assert outcome.exception is None
    assert seqs(outcome) == [42]
    assert server.state(method).connections == 2


@pytest.mark.asyncio
async def test_async_delivers_parsed_commits(server: JetstreamTestServer) -> None:
    method = server.new_method('three_commits_then_close')

    outcome = await run_async(server, method, stop_after=3)

    assert outcome.exception is None
    assert seqs(outcome) == [1, 2, 3]
    assert outcome.cursor == 3


@pytest.mark.asyncio
async def test_async_reconnect_resumes_from_the_cursor_and_dedups(server: JetstreamTestServer) -> None:
    method = server.new_method('redelivers_on_reconnect')

    outcome = await run_async(server, method, stop_after=3)

    assert seqs(outcome) == [10, 11, 12]
    assert server.state(method).queries[1]['cursor'] == ['11']


@pytest.mark.asyncio
async def test_async_undecodable_frames_are_skipped(server: JetstreamTestServer) -> None:
    method = server.new_method('garbage_between_commits')

    outcome = await run_async(server, method, stop_after=2)

    assert outcome.exception is None
    assert seqs(outcome) == [1, 3]


@pytest.mark.parametrize('client_class', [JetstreamClient, AsyncJetstreamClient])
def test_repeated_filters_are_sent_as_repeated_params(client_class: t.Any) -> None:
    client = client_class(params={'collections': ['app.bsky.feed.post', 'app.bsky.feed.like'], 'kinds': ['commit']})

    assert 'collections=app.bsky.feed.post&collections=app.bsky.feed.like' in client._websocket_uri
    assert 'kinds=commit' in client._websocket_uri


@pytest.mark.parametrize('client_class', [JetstreamClient, AsyncJetstreamClient])
def test_collections_filter_without_commit_kind_is_rejected(client_class: t.Any) -> None:
    with pytest.raises(JetstreamError):
        client_class(params={'collections': ['app.bsky.feed.post'], 'kinds': ['identity']})


@pytest.mark.parametrize('client_class', [JetstreamClient, AsyncJetstreamClient])
def test_params_are_copied_from_the_caller(client_class: t.Any) -> None:
    params = {'kinds': ['commit'], 'cursor': 5}
    client = client_class(params=params)

    client._track_cursor(42)

    assert params['cursor'] == 5


@pytest.mark.parametrize('client_class', [JetstreamClient, AsyncJetstreamClient])
def test_defaults_to_the_v2_host_and_nsid(client_class: t.Any) -> None:
    client = client_class()

    assert client._websocket_uri == ('wss://jetstream.us-east.bsky.network/xrpc/network.bsky.jetstream.subscribeEvents')


def test_cursor_too_old_is_fatal(server: JetstreamTestServer) -> None:
    method = server.new_method('cursor_too_old')

    outcome = run_sync(server, method, params={'cursor': 1}, stop_after=1)

    assert isinstance(outcome.exception, JetstreamCursorTooOldError)
    assert server.state(method).rejections == 1


def test_other_client_errors_are_fatal(server: JetstreamTestServer) -> None:
    method = server.new_method('invalid_request')

    outcome = run_sync(server, method, stop_after=1)

    assert isinstance(outcome.exception, JetstreamError)
    assert not isinstance(outcome.exception, JetstreamCursorTooOldError)
    assert server.state(method).rejections == 1


def test_server_errors_are_retried(server: JetstreamTestServer) -> None:
    method = server.new_method('server_error_then_ok')

    outcome = run_sync(server, method, stop_after=1)

    assert outcome.exception is None
    assert seqs(outcome) == [42]
    assert server.state(method).rejections == 1


@pytest.mark.asyncio
async def test_async_cursor_too_old_is_fatal(server: JetstreamTestServer) -> None:
    method = server.new_method('cursor_too_old')

    outcome = await run_async(server, method, params={'cursor': 1}, stop_after=1)

    assert isinstance(outcome.exception, JetstreamCursorTooOldError)
    assert server.state(method).rejections == 1


def test_compression_is_negotiated_and_frames_decode(server: JetstreamTestServer) -> None:
    method = server.new_method('compressed')

    outcome = run_sync(server, method, stop_after=3, compress=True)

    assert outcome.exception is None
    assert outcome.compressed
    assert seqs(outcome) == [1, 2, 3]
    assert first_commit(outcome).collection == 'app.bsky.feed.post'

    expected_id = str(DICTIONARIES['current'].dict_id())
    assert server.state(method).queries[0]['zstdDictionary'] == [expected_id]
    assert server.state(method).dictionary_fetches == 1


def test_compression_off_sends_no_dictionary_param(server: JetstreamTestServer) -> None:
    method = server.new_method('compressed')

    outcome = run_sync(server, method, stop_after=3, compress=False)

    assert not outcome.compressed
    assert seqs(outcome) == [1, 2, 3]
    assert 'zstdDictionary' not in server.state(method).queries[0]
    assert server.state(method).dictionary_fetches == 0


def test_undecompressable_frame_is_skipped(server: JetstreamTestServer) -> None:
    method = server.new_method('compressed_garbage')

    outcome = run_sync(server, method, stop_after=2, compress=True)

    assert outcome.exception is None
    assert seqs(outcome) == [1, 3]


def test_rotated_dictionary_is_refetched(server: JetstreamTestServer) -> None:
    method = server.new_method('dict_rotate')

    outcome = run_sync(server, method, stop_after=3, compress=True)

    assert outcome.exception is None
    assert outcome.compressed
    assert seqs(outcome) == [1, 2, 3]
    # fetched once before the refused dial, once more after it
    assert server.state(method).dictionary_fetches == 2
    assert server.state(method).queries[0]['zstdDictionary'] == [str(DICTIONARIES['rotated'].dict_id())]


def test_stale_dictionary_sheds_compression(server: JetstreamTestServer) -> None:
    method = server.new_method('dict_stale')

    outcome = run_sync(server, method, stop_after=3, compress=True)

    # the server keeps refusing and keeps returning the same id, so the client gives up on
    # compression and carries on with an uncompressed tail
    assert outcome.exception is None
    assert not outcome.compressed
    assert seqs(outcome) == [1, 2, 3]
    assert 'zstdDictionary' not in server.state(method).queries[0]


def test_unavailable_dictionary_sheds_compression(server: JetstreamTestServer) -> None:
    method = server.new_method('dict_unavailable')

    outcome = run_sync(server, method, stop_after=3, compress=True)

    assert outcome.exception is None
    assert not outcome.compressed
    assert seqs(outcome) == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_compression_is_negotiated(server: JetstreamTestServer) -> None:
    method = server.new_method('compressed')

    outcome = await run_async(server, method, stop_after=3, compress=True)

    assert outcome.exception is None
    assert outcome.compressed
    assert seqs(outcome) == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_unavailable_dictionary_sheds_compression(server: JetstreamTestServer) -> None:
    method = server.new_method('dict_unavailable')

    outcome = await run_async(server, method, stop_after=3, compress=True)

    assert outcome.exception is None
    assert not outcome.compressed
    assert seqs(outcome) == [1, 2, 3]
