import asyncio
import signal
import time
from collections import defaultdict
from types import FrameType
from typing import Callable, Optional, TypedDict, TypeVar, Union

from atproto import (
    CAR,
    AsyncFirehoseSubscribeReposClient,
    AtUri,
    firehose_models,
    models,
    parse_subscribe_repos_message,
)

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


async def signal_handler(_: int, __: Optional[FrameType]) -> None:
    print('Keyboard interrupt received. Stopping...')

    # Stop receiving new messages
    await client.stop()


async def main(firehose_client: AsyncFirehoseSubscribeReposClient) -> None:
    @measure_events_per_second
    async def on_message_handler(message: firehose_models.MessageFrame) -> None:
        commit = parse_subscribe_repos_message(message)
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        if commit.seq % 20 == 0:
            firehose_client.update_params(models.ComAtprotoSyncSubscribeRepos.Params(cursor=commit.seq))

        if not commit.blocks:
            return

        ops = _get_ops_by_type(commit)
        for created_post in ops[models.ids.AppBskyFeedPost]['created']:
            author = created_post['author']
            record = created_post['record']
            if not isinstance(record, models.AppBskyFeedPost.Record):
                continue

            inlined_text = record.text.replace('\n', ' ')
            print(f'NEW POST [CREATED_AT={record.created_at}][AUTHOR={author}]: {inlined_text}')

    await client.start(on_message_handler)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda _, __: asyncio.create_task(signal_handler(_, __)))

    start_cursor = None

    params = None
    if start_cursor is not None:
        params = models.ComAtprotoSyncSubscribeRepos.Params(cursor=start_cursor)

    client = AsyncFirehoseSubscribeReposClient(params)

    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main(client))
