import typing as t
from dataclasses import dataclass

from atproto_crypto.algs.p256 import P256
from atproto_crypto.algs.secp256k1 import Secp256k1
from atproto_crypto.consts import (
    BASE58_MULTIBASE_PREFIX,
    DID_KEY_PREFIX,
    P256_DID_PREFIX,
    P256_JWT_ALG,
    SECP256K1_DID_PREFIX,
    SECP256K1_JWT_ALG,
)
from atproto_crypto.exceptions import IncorrectMultikeyPrefixError, UnsupportedKeyTypeError
from atproto_crypto.multibase import bytes_to_multibase, multibase_to_bytes


@dataclass
class Multikey:
    jwt_alg: str
    key_bytes: bytes


def parse_multikey(multikey: str) -> Multikey:
    if not multikey.startswith(BASE58_MULTIBASE_PREFIX):
        raise IncorrectMultikeyPrefixError(f'Incorrect prefix for multikey {multikey}')

    prefixed_bytes = multibase_to_bytes(multikey)
    if prefixed_bytes.startswith(P256_DID_PREFIX):
        jwt_alg = P256_JWT_ALG
        compressed_key_bytes = prefixed_bytes[len(P256_DID_PREFIX) :]
        key_bytes = P256().decompress_pubkey(compressed_key_bytes)
    elif prefixed_bytes.startswith(SECP256K1_DID_PREFIX):
        jwt_alg = SECP256K1_JWT_ALG
        compressed_key_bytes = prefixed_bytes[len(SECP256K1_DID_PREFIX) :]
        key_bytes = Secp256k1().decompress_pubkey(compressed_key_bytes)
    else:
        raise UnsupportedKeyTypeError('Unsupported key type')

    return Multikey(jwt_alg, key_bytes)


def format_multikey(jwt_alg: str, key_bytes: bytes) -> str:
    if jwt_alg == P256_JWT_ALG:
        prefix = P256_DID_PREFIX
        compressed_key_bytes = P256().compress_pubkey(key_bytes)
    elif jwt_alg == SECP256K1_JWT_ALG:
        prefix = SECP256K1_DID_PREFIX
        compressed_key_bytes = Secp256k1().compress_pubkey(key_bytes)
    else:
        raise UnsupportedKeyTypeError('Unsupported key type')

    prefixed_bytes = prefix + compressed_key_bytes
    return bytes_to_multibase(BASE58_MULTIBASE_PREFIX, prefixed_bytes)


def format_did_key(jwt_alg: str, key_bytes: bytes) -> str:
    return f'{DID_KEY_PREFIX}{format_multikey(jwt_alg, key_bytes)}'


def get_did_key(key_type: str, key: str) -> t.Optional[str]:
    did_key = None
    if key_type == 'EcdsaSecp256r1VerificationKey2019':
        key_bytes = multibase_to_bytes(key)
        did_key = format_did_key(P256_JWT_ALG, key_bytes)
    elif key_type == 'EcdsaSecp256k1VerificationKey2019':
        key_bytes = multibase_to_bytes(key)
        did_key = format_did_key(SECP256K1_JWT_ALG, key_bytes)
    elif key_type == 'Multikey':
        parsed_key = parse_multikey(key)
        did_key = format_did_key(parsed_key.jwt_alg, parsed_key.key_bytes)

    return did_key
