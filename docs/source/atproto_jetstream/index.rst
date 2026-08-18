Jetstream (data streaming)
==========================

`Jetstream <https://github.com/bluesky-social/jetstream>`_ is a streaming service for the AT Protocol network. Unlike the Firehose, it delivers records as plain JSON, filters server-side, and needs no CAR or DAG-CBOR decoding.

.. note::
    Only the Jetstream v2 wire is supported. The legacy v1 hosts (``jetstream1.*``, ``jetstream2.*``) speak a different, frozen protocol and will not work with this client.

.. note::
    Jetstream carries no repository signatures or MST proofs, so its data cannot be cryptographically verified. Use :obj:`atproto.FirehoseSubscribeReposClient` when verifiability matters.

Both clients are present in two variants: sync and async. Filters are applied by the server, so you receive only what you asked for:

..  code-block:: python

    from atproto import JetstreamClient, models

    client = JetstreamClient(params={'collections': [models.ids.AppBskyFeedPost], 'kinds': ['commit']})


    def on_message_handler(event) -> None:
        if not isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Commit):
            return

        if event.operation == 'create':
            # already decoded into a model; a non-conforming record falls back to DotDict
            print(event.seq, event.record.text)


    client.start(on_message_handler)

The record arrives as JSON, so no CAR or DAG-CBOR decoding is needed.

Filtering
---------

The three filters are independent and combined with AND. Each matches everything when omitted:

- ``kinds``: ``commit``, ``identity``, ``account``, ``sync``.
- ``dids``: repositories to receive events for. Applies to every kind.
- ``collections``: NSIDs or ``<prefix>.*`` patterns.

.. warning::
    ``collections`` constrains **commit events only**. Identity, account, and sync events are delivered regardless of it, because they are the only signals telling you an account was deactivated or deleted. Pass ``kinds=['commit']`` to get a commits-only stream.

Cursor and reconnects
---------------------

The cursor is tracked for you. Reconnects resume from the last delivered event, and events the server replays are dropped before reaching your callback, so you never see a gap or a duplicate.

Persist :obj:`cursor` to resume across restarts:

..  code-block:: python

    from atproto import JetstreamClient

    client = JetstreamClient(params={'cursor': load_my_cursor()})


    def on_message_handler(event) -> None:
        ...
        save_my_cursor(client.cursor)


    client.start(on_message_handler)

.. note::
    Cursors are instance-local and are not portable between servers or between Jetstream versions.

Compression
-----------

Frames are compressed by default using Jetstream's dict-zstd scheme, which cuts bandwidth by roughly 60%. The client fetches the server's dictionary over HTTPS once at startup, negotiates it on the websocket, and decompresses each frame transparently. Your callback sees the same models either way.

..  code-block:: python

    client = JetstreamClient()
    print(client.compressed)  # False until the first connection negotiates it

Compression is best-effort and never fatal. If the dictionary cannot be fetched, or the server rotates it and the new one cannot be obtained, the client falls back to an uncompressed stream and keeps running. Check :obj:`compressed` to see what the current connection negotiated.

Pass ``compress=False`` to disable it:

..  code-block:: python

    client = JetstreamClient(compress=False)

.. note::
    Decompression costs roughly 2 microseconds per frame, about 12% of the time spent turning a frame into a model.

Archive replay
--------------

Jetstream keeps the whole network's history and can replay it. Pass an ``api_key`` and use :obj:`snapshot` for the sealed archive, or :obj:`replay` to sweep the archive and continue into the live tail without a gap:

..  code-block:: python

    from atproto import JetstreamClient

    client = JetstreamClient(params={'dids': ['did:plc:...']}, api_key='...')

    # the archive, then stop
    for event in client.snapshot(after_seq=0):
        print(event.seq, event.did)

    # the archive, then the live tail, seamlessly
    for event in client.replay(after_seq=0):
        print(event.seq, event.did)

Both yield the same models the live tail delivers, so a consumer cannot tell whether an event came from a segment or the socket. The async client mirrors this with ``async for``.

Record CIDs are not stored in the archive; the client derives each one from the record's CBOR, matching what the PDS reports.

.. note::
    Get a key at `bsky.network/account <https://bsky.network/account>`_. It is **not** an AT Protocol credential: a PDS session token and a ``com.atproto.server.getServiceAuth`` token are both rejected. The key is used only for the archive, never on the websocket, and a self-hosted Jetstream needs none.

Metering
--------

.. warning::
    The archive is **metered in bytes downloaded**, not requests. The whole network is roughly 1.85 TB. Check :obj:`bytes_downloaded` to see what a sweep cost.

What a filter costs depends on how *selective* it is, not on whether one is set. Every filter is sent to the planner, but segments carry per-DID bloom filters, so ``dids`` prunes hard while a popular collection appears in nearly every block and prunes almost nothing. Planning the whole archive:

===============================================  ==========================  ===========
filter                                           segments matched            blocks
===============================================  ==========================  ===========
``dids=['did:plc:...']``                         1 of 7,075                  1
``collections=['app.bsky.feed.post']``           7,075 of 7,075              5,363,406
===============================================  ==========================  ===========

To follow a busy collection, resume from a stored cursor rather than sweeping from ``after_seq=0``.

The client honours the plan's download mode, so a sparse filter fetches individual blocks rather than whole 261 MB segments, and whole segments are read in HTTP ``Range`` slices so they never land in memory at once. If the quota is exhausted the server replies ``429`` with ``Retry-After``, and the client waits it out rather than retrying blindly.

More code examples: https://github.com/MarshalX/atproto/tree/main/examples/jetstream

.. automodule:: atproto_jetstream
   :members:
   :undoc-members:
   :inherited-members:

Submodules
----------

.. toctree::
   :maxdepth: 4

   models
   archive
