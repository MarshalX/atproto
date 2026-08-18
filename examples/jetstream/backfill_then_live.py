"""Catch up on the archive, then keep streaming live, without a gap or a duplicate.

`replay()` sweeps the sealed archive first and cuts over to the live tail at the seam. It
never terminates.

The archive is metered in bytes, and how much a filter costs depends on how selective it is,
not on whether one is set. Every filter is sent to the planner, but segments carry per-DID
bloom filters: `dids` prunes hard, while a popular collection appears in nearly every block
and prunes almost nothing.

Measured against the whole archive, from `after_seq=0`:

    dids=[one repo]                    ->        1 of 7,075 segments,         1 block
    collections=[app.bsky.feed.post]   ->    7,075 of 7,075 segments, 5,363,406 blocks

So this example filters to one repository. Its whole history is a single block, about
274 KB. To follow a busy collection instead, resume from a stored cursor rather than
sweeping from the beginning.
"""

import os

from atproto import JetstreamClient, models

TARGET_DID = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'

client = JetstreamClient(params={'dids': [TARGET_DID]}, api_key=os.environ['JETSTREAM_API_KEY'])

# archived events arrive first, then the stream continues live from the seam
for event in client.replay(after_seq=0):
    if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
        continue

    print(f'{event.seq} {event.collection} {event.operation}')
