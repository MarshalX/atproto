"""Replay one repository's whole history out of the Jetstream archive.

Needs an API key from https://bsky.network/account. The archive is metered in bytes, so
filter narrowly: this plan matches a single block.
"""

import os

from atproto import JetstreamClient, models

TARGET_DID = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'

client = JetstreamClient(params={'dids': [TARGET_DID]}, api_key=os.environ['JETSTREAM_API_KEY'])

posts = 0
for event in client.snapshot(after_seq=0):
    if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
        continue

    if event.collection != models.ids.AppBskyFeedPost or event.operation != 'create':
        continue

    posts += 1
    print(f'[{event.seq}] {event.time} {event.record.text[:60]}')

print(f'\n{posts} posts, {client.bytes_downloaded:,} bytes downloaded')
