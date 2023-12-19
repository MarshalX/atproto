Firehose (data streaming)
=========================

You can use the clients below to get real-time updates from the whole network. If you subscribe to retrieve messages from repositories you will get information about each created, deleted, liked, reposted post, etc.

All clients present in two variants: sync and async. As a developer, you should create your own callback on a new message to handle incoming data. Here is how to do it:

..  code-block:: python

    from atproto_firehose import FirehoseSubscribeReposClient, parse_subscribe_repos_message

    client = FirehoseSubscribeReposClient()


    def on_message_handler(message) -> None:
        print(message.header, parse_subscribe_repos_message(message))


    client.start(on_message_handler)

More code examples: https://github.com/MarshalX/atproto/tree/main/examples/firehose

.. note::
    To achieve more performance you could parse only required messages using `message.header` to filter.

By default :obj:`parse_subscribe_repos_message` and :obj:`parse_subscribe_labels_message` doesn't decode inner DAG-CBOR. Probably you want to decode it. To do so use :obj:`atproto.CAR`. Example of message handler with decoding of CAR files (commit blocks):

..  code-block:: python

    from atproto import CAR, models

    def on_message_handler(message) -> None:
        commit = parse_subscribe_repos_message(message)
        # we need to be sure that it's commit message with .blocks inside
        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        car = CAR.from_bytes(commit.blocks)

.. automodule:: atproto_firehose
   :members:
   :undoc-members:
   :inherited-members:

Submodules
----------

.. toctree::
   :maxdepth: 4

   atproto_firehose.models
