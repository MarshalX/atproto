from atproto import FirehoseSubscribeReposClient, firehose_models, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()


def on_message_handler(message: firehose_models.MessageFrame) -> None:
    print(message.header, parse_subscribe_repos_message(message))


client.start(on_message_handler)
