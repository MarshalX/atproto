from dataclasses import dataclass

from atproto_crypto.consts import (
    BASE58_MULTIBASE_PREFIX,
    DID_KEY_PREFIX,
    P256_DID_PREFIX,
    P256_JWT_ALG,
    SECP256K1_DID_PREFIX,
    SECP256K1_JWT_ALG,
)
from atproto_crypto.multibase import bytes_to_multibase, multibase_to_bytes
from atproto_crypto.p256.encoding import compress_public_key as p256_compress_public_key
from atproto_crypto.p256.encoding import decompress_public_key as p256_decompress_public_key
from atproto_crypto.secp256k1.encoding import compress_public_key as secp256k1_compress_public_key
from atproto_crypto.secp256k1.encoding import decompress_public_key as secp256k1_decompress_public_key


@dataclass
class Multikey:
    jwt_alg: str
    key_bytes: bytes


def parse_multikey(multikey: str) -> Multikey:
    if not multikey.startswith(BASE58_MULTIBASE_PREFIX):
        raise ValueError(f'Incorrect prefix for multikey {multikey}')

    prefixed_bytes = multibase_to_bytes(multikey)

    if prefixed_bytes.startswith(P256_DID_PREFIX):
        jwt_alg = P256_JWT_ALG
        compressed_key_bytes = prefixed_bytes[len(P256_DID_PREFIX) :]
        key_bytes = p256_decompress_public_key(compressed_key_bytes)
    elif prefixed_bytes.startswith(SECP256K1_DID_PREFIX):
        jwt_alg = SECP256K1_JWT_ALG
        compressed_key_bytes = prefixed_bytes[len(SECP256K1_DID_PREFIX) :]
        key_bytes = secp256k1_decompress_public_key(compressed_key_bytes)
    else:
        raise ValueError('Unsupported key type')

    return Multikey(jwt_alg, key_bytes)


def format_multikey(jwt_alg: str, key_bytes: bytes) -> str:
    if jwt_alg == P256_JWT_ALG:
        prefix = P256_DID_PREFIX
        compressed_key_bytes = p256_compress_public_key(key_bytes)
    elif jwt_alg == SECP256K1_JWT_ALG:
        prefix = SECP256K1_DID_PREFIX
        compressed_key_bytes = secp256k1_compress_public_key(key_bytes)
    else:
        raise ValueError('Unsupported key type')

    prefixed_bytes = prefix + compressed_key_bytes
    return bytes_to_multibase(BASE58_MULTIBASE_PREFIX, prefixed_bytes)


def format_did_key(jwt_alg: str, key_bytes: bytes) -> str:
    return f'{DID_KEY_PREFIX}{format_multikey(jwt_alg, key_bytes)}'
