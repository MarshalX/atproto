import asyncio

from atproto import (
    AsyncFirehoseSubscribeReposClient,
    firehose_models,
    parse_subscribe_repos_message,
)


async def main() -> None:
    client = AsyncFirehoseSubscribeReposClient()

    async def on_message_handler(message: firehose_models.MessageFrame) -> None:
        print(message.header, parse_subscribe_repos_message(message))

    await client.start(on_message_handler)


if __name__ == '__main__':
    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main())
