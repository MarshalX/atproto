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
            post = models.get_or_create(event.record, models.AppBskyFeedPost.Record)
            print(event.seq, post.text)


    client.start(on_message_handler)

The record arrives as JSON, so no CAR or DAG-CBOR decoding is needed.

Filtering
---------

The three filters are independent and combined with AND. Each matches everything when omitted:

- ``kinds`` — ``commit``, ``identity``, ``account``, ``sync``.
- ``dids`` — repositories to receive events for. Applies to every kind.
- ``collections`` — NSIDs or ``<prefix>.*`` patterns.

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

Backfill
--------

This package covers the live tail. Historical replay is not implemented: it needs a reader for Jetstream's binary segment format, and the archive endpoints require a bearer token on the hosted instance.

The archive XRPC methods themselves are generated and reachable, so you can drive them yourself. Pass your own credential per call:

..  code-block:: python

    from atproto import Client, models

    client = Client(base_url='https://jetstream.us-east.bsky.network')
    auth = {'Authorization': 'Bearer <your-api-key>'}

    plan = client.network.bsky.jetstream.plan_snapshot(
        {'collections': [models.ids.AppBskyFeedPost], 'kinds': ['commit'], 'after_seq': 0},
        headers=auth,
    )
    for segment in plan.segments:
        print(segment.name, segment.min_seq, segment.max_seq)

Decoding the downloaded ``.jss`` segments is up to you. ``getZstdDictionary`` is public and needs no credential.

.. warning::
    The archive key is **not** an AT Protocol credential. It is an opaque bearer token issued by whoever operates the instance.

.. automodule:: atproto_jetstream
   :members:
   :undoc-members:
   :inherited-members:

Submodules
----------

.. toctree::
   :maxdepth: 4

   models
