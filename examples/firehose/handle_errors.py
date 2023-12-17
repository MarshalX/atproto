from atproto.firehose import FirehoseSubscribeReposClient, MessageFrame, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()


def on_message_handler(message: MessageFrame) -> None:
    print(message.header, parse_subscribe_repos_message(message))
    raise ValueError('Failed to process message')


def on_callback_error_handler(error: BaseException) -> None:
    print('Got error!', error)


client.start(on_message_handler, on_callback_error_handler)
