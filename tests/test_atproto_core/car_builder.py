"""Builds CAR files in memory so tests never need captured network data."""

import hashlib
import typing as t

import libipld

_CID_V1 = b'\x01'
_DAG_CBOR = b'\x71'
_SHA2_256 = b'\x12\x20'  # multihash code 0x12, digest length 0x20


def make_cid(block: bytes) -> bytes:
    """Binary CIDv1 of a DAG-CBOR block: its sha2-256 digest."""
    return _CID_V1 + _DAG_CBOR + _SHA2_256 + hashlib.sha256(block).digest()


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | 0x80 if value else byte)
        if not value:
            return bytes(out)


def _cbor_cid_link(cid: bytes) -> bytes:
    """DAG-CBOR tag 42 around the CID, identity-multibase prefixed."""
    body = b'\x00' + cid
    return b'\xd8\x2a\x58' + bytes([len(body)]) + body


def _header(root: bytes) -> bytes:
    """DAG-CBOR ``{'roots': [root], 'version': 1}``, keys in canonical order."""
    return b'\xa2\x65roots\x81' + _cbor_cid_link(root) + b'\x67version\x01'


def encode_car(blocks: t.Sequence[dict]) -> bytes:
    """Encode blocks as a CARv1 file rooted at the first one."""
    encoded = [libipld.encode_dag_cbor(block) for block in blocks]
    cids = [make_cid(block) for block in encoded]

    parts = [_header(cids[0])]
    parts = [_varint(len(parts[0])), *parts]
    for cid, block in zip(cids, encoded):
        parts.append(_varint(len(cid) + len(block)))
        parts.append(cid)
        parts.append(block)

    return b''.join(parts)
