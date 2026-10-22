"""The AT Protocol SDK.

Names are imported on first access, so ``from atproto import Client`` does not load the firehose,
Jetstream, identity, crypto, and server packages.
"""

import typing as t

from atproto_core.lazy_exports import lazy_exports

if t.TYPE_CHECKING:
    from atproto_client import AsyncClient, Client, Session, SessionEvent, models
    from atproto_client import utils as client_utils
    from atproto_client.request import AsyncRequest, Request
    from atproto_core.car import CAR
    from atproto_core.cid import CID, CIDType
    from atproto_core.did_doc import DidDocument
    from atproto_core.nsid import NSID
    from atproto_core.uri import AtUri
    from atproto_crypto.did import Multikey, get_did_key
    from atproto_crypto.multibase import bytes_to_multibase, multibase_to_bytes
    from atproto_crypto.verify import verify_signature
    from atproto_firehose import (
        AsyncFirehoseSubscribeLabelsClient,
        AsyncFirehoseSubscribeReposClient,
        FirehoseSubscribeLabelsClient,
        FirehoseSubscribeReposClient,
        parse_subscribe_labels_message,
        parse_subscribe_repos_message,
    )
    from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache, DidInMemoryCache
    from atproto_identity.did.atproto_data import AtprotoData
    from atproto_identity.resolver import AsyncIdResolver, IdResolver
    from atproto_jetstream import (
        AsyncJetstreamClient,
        JetstreamClient,
        parse_subscribe_events_message,
    )
    from atproto_jetstream import archive as jetstream_archive
    from atproto_jetstream import models as jetstream_models
    from atproto_server.auth.jwt import (
        JwtPayload,
        decode_jwt_payload,
        get_jwt_payload,
        parse_jwt,
        validate_jwt_payload,
        verify_jwt,
        verify_jwt_async,
    )
    from atproto_subscription import frames as firehose_models

__getattr__, __dir__ = lazy_exports(
    __name__,
    attributes={
        'atproto_client': ('AsyncClient', 'Client', 'Session', 'SessionEvent'),
        'atproto_client.request': ('AsyncRequest', 'Request'),
        'atproto_core.car': ('CAR',),
        'atproto_core.cid': ('CID', 'CIDType'),
        'atproto_core.did_doc': ('DidDocument',),
        'atproto_core.nsid': ('NSID',),
        'atproto_core.uri': ('AtUri',),
        'atproto_crypto.did': ('Multikey', 'get_did_key'),
        'atproto_crypto.multibase': ('bytes_to_multibase', 'multibase_to_bytes'),
        'atproto_crypto.verify': ('verify_signature',),
        'atproto_firehose': (
            'AsyncFirehoseSubscribeLabelsClient',
            'AsyncFirehoseSubscribeReposClient',
            'FirehoseSubscribeLabelsClient',
            'FirehoseSubscribeReposClient',
            'parse_subscribe_labels_message',
            'parse_subscribe_repos_message',
        ),
        'atproto_identity.cache.in_memory_cache': ('AsyncDidInMemoryCache', 'DidInMemoryCache'),
        'atproto_identity.did.atproto_data': ('AtprotoData',),
        'atproto_identity.resolver': ('AsyncIdResolver', 'IdResolver'),
        'atproto_jetstream': ('AsyncJetstreamClient', 'JetstreamClient', 'parse_subscribe_events_message'),
        'atproto_server.auth.jwt': (
            'JwtPayload',
            'decode_jwt_payload',
            'get_jwt_payload',
            'parse_jwt',
            'validate_jwt_payload',
            'verify_jwt',
            'verify_jwt_async',
        ),
    },
    modules={
        'models': 'atproto_client.models',
        'client_utils': 'atproto_client.utils',
        'firehose_models': 'atproto_subscription.frames',
        'jetstream_archive': 'atproto_jetstream.archive',
        'jetstream_models': 'atproto_jetstream.models',
    },
)

__all__ = [  # noqa: RUF022
    # client
    'AsyncClient',
    'Client',
    'SessionEvent',
    'Session',
    'client_utils',
    'models',
    'Request',
    'AsyncRequest',
    # core
    'CAR',
    'CID',
    'CIDType',
    'DidDocument',
    'NSID',
    'AtUri',
    # crypto
    'bytes_to_multibase',
    'get_did_key',
    'multibase_to_bytes',
    'Multikey',
    'verify_signature',
    # firehose
    'AsyncFirehoseSubscribeLabelsClient',
    'AsyncFirehoseSubscribeReposClient',
    'FirehoseSubscribeLabelsClient',
    'FirehoseSubscribeReposClient',
    'parse_subscribe_labels_message',
    'parse_subscribe_repos_message',
    'firehose_models',
    # jetstream
    'AsyncJetstreamClient',
    'JetstreamClient',
    'parse_subscribe_events_message',
    'jetstream_models',
    'jetstream_archive',
    # identity
    'AtprotoData',
    'AsyncDidInMemoryCache',
    'DidInMemoryCache',
    'AsyncIdResolver',
    'IdResolver',
    # server jwt
    'JwtPayload',
    'decode_jwt_payload',
    'get_jwt_payload',
    'parse_jwt',
    'validate_jwt_payload',
    'verify_jwt',
    'verify_jwt_async',
]
