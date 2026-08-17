from atproto import JetstreamClient, jetstream_models, models

client = JetstreamClient(params={'collections': [models.ids.AppBskyFeedPost], 'kinds': ['commit']})


def on_message_handler(event: jetstream_models.SubscribeEventsMessage) -> None:
    if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
        return

    if event.operation != 'create':
        return

    # already decoded into a model by the client; a non-conforming record falls back to DotDict
    print(f'[{event.seq}] {event.did}: {event.record.text}')


client.start(on_message_handler)
