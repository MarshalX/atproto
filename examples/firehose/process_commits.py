import multiprocessing
import signal
import sys
import time
from collections import defaultdict
from types import FrameType
from typing import TYPE_CHECKING, Callable, Optional, TypedDict, TypeVar, Union

from atproto import CAR, AtUri, FirehoseSubscribeReposClient, firehose_models, models, parse_subscribe_repos_message

if TYPE_CHECKING:
    from multiprocessing.queues import Queue
    from multiprocessing.sharedctypes import Synchronized

R = TypeVar('R')


InterestedRecord = Union[models.AppBskyFeedLike.Record, models.AppBskyFeedPost.Record, models.AppBskyGraphFollow.Record]

_INTERESTED_RECORDS: dict[str, type[InterestedRecord]] = {
    models.ids.AppBskyFeedLike: models.AppBskyFeedLike.Record,
    models.ids.AppBskyFeedPost: models.AppBskyFeedPost.Record,
    models.ids.AppBskyGraphFollow: models.AppBskyGraphFollow.Record,
}


class CreatedOp(TypedDict):
    record: InterestedRecord
    uri: str
    cid: str
    author: str


class Ops(TypedDict):
    created: list[CreatedOp]
    deleted: list[dict[str, str]]


def _get_ops_by_type(commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> defaultdict[str, Ops]:
    operation_by_type: defaultdict[str, Ops] = defaultdict(lambda: {'created': [], 'deleted': []})

    car = CAR.from_bytes(commit.blocks)
    for op in commit.ops:
        if op.action == 'update':
            # not supported yet
            continue

        uri = AtUri.from_str(f'at://{commit.repo}/{op.path}')

        if op.action == 'create':
            if not op.cid:
                continue

            record_raw_data = car.blocks.get(op.cid)
            if not record_raw_data:
                continue

            record = models.get_or_create(record_raw_data, strict=False)
            record_type = _INTERESTED_RECORDS.get(uri.collection)
            if record_type and models.is_record_type(record, record_type):
                operation_by_type[uri.collection]['created'].append(
                    {'record': record, 'uri': str(uri), 'cid': str(op.cid), 'author': commit.repo}
                )

        if op.action == 'delete':
            operation_by_type[uri.collection]['deleted'].append({'uri': str(uri)})

    return operation_by_type


def worker_main(cursor_value: 'Synchronized[int]', pool_queue: 'Queue[firehose_models.MessageFrame]') -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # we handle it in the main process

    while True:
        message = pool_queue.get()

        commit = parse_subscribe_repos_message(message)
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            continue

        if commit.seq % 20 == 0:
            cursor_value.value = commit.seq

        if not commit.blocks:
            continue

        ops = _get_ops_by_type(commit)
        for created_post in ops[models.ids.AppBskyFeedPost]['created']:
            author = created_post['author']
            record = created_post['record']
            if not isinstance(record, models.AppBskyFeedPost.Record):
                continue

            inlined_text = record.text.replace('\n', ' ')
            print(f'NEW POST [CREATED_AT={record.created_at}][AUTHOR={author}]: {inlined_text}')


def get_firehose_params(cursor_value: 'Synchronized[int]') -> models.ComAtprotoSyncSubscribeRepos.Params:
    return models.ComAtprotoSyncSubscribeRepos.Params(cursor=cursor_value.value)


def measure_events_per_second(
    func: Callable[[firehose_models.MessageFrame], R],
) -> Callable[[firehose_models.MessageFrame], R]:
    calls = 0
    start_time = time.time()

    def wrapper(message: firehose_models.MessageFrame) -> R:
        nonlocal calls, start_time
        calls += 1
        cur_time = time.time()

        if cur_time - start_time >= 1:
            print(f'NETWORK LOAD: {calls} events/second')
            start_time = cur_time
            calls = 0

        return func(message)

    return wrapper


def signal_handler(_: int, __: Optional[FrameType]) -> None:
    print('Keyboard interrupt received. Waiting for the queue to empty before terminating processes...')

    # Stop receiving new messages
    client.stop()

    # Drain the messages queue
    while not queue.empty():
        print('Waiting for the queue to empty...')
        time.sleep(0.2)

    print('Queue is empty. Gracefully terminating processes...')

    pool.terminate()
    pool.join()

    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    start_cursor = None

    params = None
    cursor = multiprocessing.Value('i', 0)
    if start_cursor is not None:
        cursor = multiprocessing.Value('i', start_cursor)
        params = get_firehose_params(cursor)

    client = FirehoseSubscribeReposClient(params)

    workers_count = multiprocessing.cpu_count() * 2 - 1
    max_queue_size = 10000

    queue: 'Queue[firehose_models.MessageFrame]' = multiprocessing.Queue(maxsize=max_queue_size)
    pool = multiprocessing.Pool(workers_count, worker_main, (cursor, queue))

    @measure_events_per_second
    def on_message_handler(message: firehose_models.MessageFrame) -> None:
        if cursor.value:
            # we are using updating the cursor state here because of multiprocessing
            # typically you can call client.update_params() directly on commit processing
            client.update_params(get_firehose_params(cursor))

        queue.put(message)

    client.start(on_message_handler)
