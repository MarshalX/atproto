from atproto import JetstreamClient, jetstream_models, models

client = JetstreamClient(params={'collections': [models.ids.AppBskyFeedPost], 'kinds': ['commit']})


def on_message_handler(event: jetstream_models.SubscribeEventsMessage) -> None:
    if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
        return

    if event.operation != 'create':
        return

    post = models.get_or_create(event.record, models.AppBskyFeedPost.Record, strict=False)
    print(f'[{event.seq}] {event.did}: {post.text}')


client.start(on_message_handler)
