import asyncio

from atproto import AsyncJetstreamClient, jetstream_models, models

client = AsyncJetstreamClient(params={'collections': [models.ids.AppBskyFeedPost], 'kinds': ['commit']})


async def on_message_handler(event: jetstream_models.SubscribeEventsMessage) -> None:
    if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
        return

    if event.operation != 'create':
        return

    # already decoded into a model by the client; a non-conforming record falls back to DotDict
    print(f'[{event.seq}] {event.did}: {event.record.text}')


asyncio.run(client.start(on_message_handler))
