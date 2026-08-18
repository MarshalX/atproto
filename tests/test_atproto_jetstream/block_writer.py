"""Writes `.jss` blocks so tests can build one in memory."""

import struct
import typing as t

import zstandard
from atproto_jetstream.archive.segment import SegmentEvent

_FIXED_COLUMNS = (
    ('seq', 'Q'),
    ('witnessed_at', 'q'),
    ('indexed_at', 'q'),
    ('kind', 'B'),
    ('collection_len', 'B'),
    ('did_len', 'H'),
    ('rkey_len', 'B'),
    ('rev_len', 'B'),
    ('event_len', 'I'),
)


def encode_columns(events: t.Sequence[SegmentEvent]) -> bytes:
    """Lay rows out in the block's columnar format, uncompressed."""
    count = len(events)
    blobs = {
        'collection': [event.collection.encode('UTF-8') for event in events],
        'did': [event.did.encode('UTF-8') for event in events],
        'rkey': [event.rkey.encode('UTF-8') for event in events],
        'rev': [event.rev.encode('UTF-8') for event in events],
        'payload': [event.payload or b'' for event in events],
    }
    values = {
        'seq': [event.seq for event in events],
        'witnessed_at': [event.witnessed_at for event in events],
        'indexed_at': [event.indexed_at for event in events],
        'kind': [event.kind for event in events],
        'collection_len': [len(blob) for blob in blobs['collection']],
        'did_len': [len(blob) for blob in blobs['did']],
        'rkey_len': [len(blob) for blob in blobs['rkey']],
        'rev_len': [len(blob) for blob in blobs['rev']],
        'event_len': [len(blob) for blob in blobs['payload']],
    }

    parts = [struct.pack('<I', count)]
    for name, fmt in _FIXED_COLUMNS:
        parts.append(struct.pack(f'<{count}{fmt}', *values[name]))

    for name in ('collection', 'did', 'rkey', 'rev', 'payload'):
        parts.append(b''.join(blobs[name]))

    return b''.join(parts)


def encode_block(events: t.Sequence[SegmentEvent]) -> bytes:
    """Build a block frame, exactly as `getBlock` would return it."""
    return zstandard.ZstdCompressor().compress(encode_columns(events))
