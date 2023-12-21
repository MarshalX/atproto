import multiprocessing

from atproto import CAR, AtUri, FirehoseSubscribeReposClient, firehose_models, models, parse_subscribe_repos_message


def _get_ops_by_type(commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> dict:  # noqa: C901
    operation_by_type = {
        'posts': {'created': [], 'deleted': []},
        'reposts': {'created': [], 'deleted': []},
        'likes': {'created': [], 'deleted': []},
        'follows': {'created': [], 'deleted': []},
    }

    car = CAR.from_bytes(commit.blocks)
    for op in commit.ops:
        uri = AtUri.from_str(f'at://{commit.repo}/{op.path}')

        if op.action == 'update':
            # not supported yet
            continue

        if op.action == 'create':
            if not op.cid:
                continue

            create_info = {'uri': str(uri), 'cid': str(op.cid), 'author': commit.repo}

            record_raw_data = car.blocks.get(op.cid)
            if not record_raw_data:
                continue

            record = models.get_or_create(record_raw_data, strict=False)
            if uri.collection == models.ids.AppBskyFeedLike and models.is_record_type(
                record, models.ids.AppBskyFeedLike
            ):
                operation_by_type['likes']['created'].append({'record': record, **create_info})
            elif uri.collection == models.ids.AppBskyFeedPost and models.is_record_type(
                record, models.ids.AppBskyFeedPost
            ):
                operation_by_type['posts']['created'].append({'record': record, **create_info})
            elif uri.collection == models.ids.AppBskyFeedRepost and models.is_record_type(
                record, models.ids.AppBskyFeedRepost
            ):
                operation_by_type['reposts']['created'].append({'record': record, **create_info})
            elif uri.collection == models.ids.AppBskyGraphFollow and models.is_record_type(
                record, models.ids.AppBskyGraphFollow
            ):
                operation_by_type['follows']['created'].append({'record': record, **create_info})

        if op.action == 'delete':
            if uri.collection == models.ids.AppBskyFeedLike:
                operation_by_type['likes']['deleted'].append({'uri': str(uri)})
            elif uri.collection == models.ids.AppBskyFeedPost:
                operation_by_type['posts']['deleted'].append({'uri': str(uri)})
            elif uri.collection == models.ids.AppBskyFeedRepost:
                operation_by_type['reposts']['deleted'].append({'uri': str(uri)})
            elif uri.collection == models.ids.AppBskyGraphFollow:
                operation_by_type['follows']['deleted'].append({'uri': str(uri)})

    return operation_by_type


def worker_main(cursor_value: multiprocessing.Value, pool_queue: multiprocessing.Queue) -> None:
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
        for post in ops['posts']['created']:
            post_msg = post['record'].text
            post_langs = post['record'].langs
            print(f'New post in the network! Langs: {post_langs}. Text: {post_msg}')


def get_firehose_params(cursor_value: multiprocessing.Value) -> models.ComAtprotoSyncSubscribeRepos.Params:
    return models.ComAtprotoSyncSubscribeRepos.Params(cursor=cursor_value.value)


if __name__ == '__main__':
    start_cursor = None

    params = None
    cursor = multiprocessing.Value('i', 0)
    if start_cursor is not None:
        cursor = multiprocessing.Value('i', start_cursor)
        params = get_firehose_params(cursor)

    client = FirehoseSubscribeReposClient(params)

    workers_count = multiprocessing.cpu_count() * 2 - 1
    max_queue_size = 500

    queue = multiprocessing.Queue(maxsize=max_queue_size)
    pool = multiprocessing.Pool(workers_count, worker_main, (cursor, queue))

    def on_message_handler(message: firehose_models.MessageFrame) -> None:
        if cursor.value:
            # we are using updating the cursor state here because of multiprocessing
            # typically you can call client.update_params() directly on commit processing
            client.update_params(get_firehose_params(cursor))

        queue.put(message)

    client.start(on_message_handler)
