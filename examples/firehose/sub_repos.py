from atproto.firehose import FirehoseSubscribeReposClient, MessageFrame, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()


def on_message_handler(message: MessageFrame) -> None:
    print(message.header, parse_subscribe_repos_message(message))


client.start(on_message_handler)
