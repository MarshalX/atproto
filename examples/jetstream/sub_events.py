from atproto import JetstreamClient, jetstream_models, models

client = JetstreamClient()


def on_message_handler(event: jetstream_models.SubscribeEventsMessage) -> None:
    if isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Info):
        # advisory about the stream itself; it carries no seq
        print('info:', event.name, event.message)
        return

    print(event.seq, event.did, type(event).__name__)


client.start(on_message_handler)
