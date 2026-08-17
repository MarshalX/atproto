"""Async archive replay.

Downloads run on the event loop and decoding is offloaded, so the loop stays responsive
while blocks are being decoded.
"""

import asyncio
import os

from atproto import AsyncJetstreamClient, models

TARGET_DID = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'


async def main() -> None:
    client = AsyncJetstreamClient(params={'dids': [TARGET_DID]}, api_key=os.environ['JETSTREAM_API_KEY'])

    collections: dict = {}
    async for event in client.snapshot(after_seq=0):
        if isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
            collections[event.collection] = collections.get(event.collection, 0) + 1

    for collection, count in sorted(collections.items(), key=lambda item: -item[1]):
        print(f'{count:5} {collection}')

    print(f'\n{client.bytes_downloaded:,} bytes downloaded')


asyncio.run(main())
