Firehose (data streaming)
=========================

You can use the clients below to get real-time updates from the whole network. If you subscribe to retrieve messages from repositories you will get information about each created, deleted, liked, reposted post, etc.

All clients present in two variants: sync and async. As a developer, you should create your own callback on a new message to handle incoming data. Here is how to do it:

..  code-block:: python

    from atproto.firehose import FirehoseSubscribeReposClient, parse_subscribe_repos_message

    client = FirehoseSubscribeReposClient()


    def on_message_handler(message) -> None:
        print(message.header, parse_subscribe_repos_message(message))


    client.start(on_message_handler)

More code examples: https://github.com/MarshalX/atproto/tree/main/examples/firehose

.. note::
    To achieve more performance you could parse only required messages using `message.header` to filter.

.. note::
    By default :obj:`parse_subscribe_repos_message` and :obj:`parse_subscribe_labels_message` decodes inner DAG-CBOR. Probably you want to decode it only on specific commit to repository. To control this behaviour you can use `decode_inner_cbor` boolean argument.

.. automodule:: atproto.firehose
   :members:
   :undoc-members:
   :inherited-members:

Submodules
----------

.. toctree::
   :maxdepth: 4

   firehose.models
