"""Builds STAR files in memory so tests never need captured network data."""

import typing as t

from atproto_core.cbor import encode_dag

_MAGIC = b'\x2a\x6c\x01\x00'
_CONTROL_END = b'\x00'
_CONTROL_PAIR = b'\x01'

_REPO_ARCHIVE_TYPE = 'atproto-space-repo'


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | 0x80 if value else byte)
        if not value:
            return bytes(out)


def _frame(data: bytes) -> bytes:
    return _varint(len(data)) + data


def encode_star(meta: bytes, pairs: t.Iterable[t.Tuple[bytes, bytes]] = ()) -> bytes:
    """Encode a STAR file from the DAG-CBOR of its metadata and its pairs, kept in the given order."""
    parts = [_MAGIC, _frame(meta)]
    for key, value in pairs:
        parts += [_CONTROL_PAIR, _frame(key), _frame(value)]

    return b''.join([*parts, _CONTROL_END])


def encode_repo_archive(commit: t.Mapping[str, t.Any], records: t.Iterable[t.Tuple[str, bytes]] = ()) -> bytes:
    """Encode the archive of a repo from its commit and the DAG-CBOR of its records by path, kept in the given order."""
    meta = encode_dag({'$type': _REPO_ARCHIVE_TYPE, **commit})

    return encode_star(meta, [(path.encode('UTF-8'), value) for path, value in records])
