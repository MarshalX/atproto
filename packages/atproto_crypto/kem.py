import hashlib
import hmac
import typing as t
from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric import ec

from atproto_crypto.algs.p256 import P256
from atproto_crypto.consts import P256_JWT_ALG
from atproto_crypto.did import parse_did_key, private_key_to_did_key
from atproto_crypto.exceptions import InvalidCompressedPubkeyError, UnsupportedKeyTypeError

_P256: t.Final = P256()

# HPKE (RFC 9180) with DHKEM(P-256, HKDF-SHA256), HKDF-SHA256 and the export-only AEAD
_HPKE_VERSION: t.Final = b'HPKE-v1'
_KEM_ID: t.Final = b'KEM\x00\x10'
_SUITE_ID: t.Final = b'HPKE\x00\x10\x00\x01\xff\xff'
_MODE_BASE: t.Final = b'\x00'

_SECRET_SIZE: t.Final = 32


@dataclass(frozen=True)
class Encapsulation:
    """Shared secret and the key share that lets the recipient derive it.

    Attributes:
        key_share: Ephemeral public key of the sender as a DID key.
        shared_secret: Shared secret of 32 bytes.
    """

    key_share: str
    shared_secret: bytes = field(repr=False)


def _labeled_extract(suite_id: bytes, salt: bytes, label: bytes, ikm: bytes) -> bytes:
    return hmac.new(salt, _HPKE_VERSION + suite_id + label + ikm, hashlib.sha256).digest()


def _labeled_expand(suite_id: bytes, prk: bytes, label: bytes, info: bytes) -> bytes:
    labeled_info = _SECRET_SIZE.to_bytes(2, 'big') + _HPKE_VERSION + suite_id + label + info
    # the output is as long as the hash, so HKDF-Expand is a single block
    return hmac.new(prk, labeled_info + b'\x01', hashlib.sha256).digest()


def _derive_shared_secret(dh: bytes, key_share: bytes, recipient: bytes, info: bytes) -> bytes:
    eae_prk = _labeled_extract(_KEM_ID, b'', b'eae_prk', dh)
    kem_secret = _labeled_expand(_KEM_ID, eae_prk, b'shared_secret', key_share + recipient)

    psk_id_hash = _labeled_extract(_SUITE_ID, b'', b'psk_id_hash', b'')
    info_hash = _labeled_extract(_SUITE_ID, b'', b'info_hash', info)
    secret = _labeled_extract(_SUITE_ID, kem_secret, b'secret', b'')
    exporter_secret = _labeled_expand(_SUITE_ID, secret, b'exp', _MODE_BASE + psk_id_hash + info_hash)

    return _labeled_expand(_SUITE_ID, exporter_secret, b'sec', b'')


def _get_public_key_bytes(did_key: str) -> bytes:
    try:
        multikey = parse_did_key(did_key)
    except (ValueError, InvalidCompressedPubkeyError) as e:
        raise UnsupportedKeyTypeError('KEM key must be a P-256 DID key') from e

    if multikey.jwt_alg != P256_JWT_ALG:
        raise UnsupportedKeyTypeError('KEM key must be a P-256 DID key')

    return multikey.key_bytes


def _exchange(private_key: ec.EllipticCurvePrivateKey, public_key: bytes) -> bytes:
    return private_key.exchange(ec.ECDH(), _P256.get_elliptic_curve_public_key(public_key))


def encapsulate(recipient: str, info: bytes) -> Encapsulation:
    """Derive a shared secret that only the holder of the recipient key can derive too.

    The secret is the one that HPKE (RFC 9180) exports in the base mode with an empty exporter context.
    Each call uses a new ephemeral key.

    Args:
        recipient: P-256 public key of the recipient as a DID key.
        info: Application info that binds the secret to its purpose.

    Returns:
        :obj:`Encapsulation`: Shared secret and the key share to send to the recipient.

    Raises:
        :class:`atproto_crypto.exceptions.DidKeyError`: The recipient is not a DID key of a P-256 key.
    """
    recipient_key = _get_public_key_bytes(recipient)

    private_key = ec.generate_private_key(ec.SECP256R1())
    key_share = private_key_to_did_key(private_key)
    shared_secret = _derive_shared_secret(
        _exchange(private_key, recipient_key), _get_public_key_bytes(key_share), recipient_key, info
    )

    return Encapsulation(key_share=key_share, shared_secret=shared_secret)


def decapsulate(private_key: ec.EllipticCurvePrivateKey, key_share: str, info: bytes) -> bytes:
    """Derive the shared secret of an encapsulation made for the given key.

    Args:
        private_key: P-256 private key of the recipient.
        key_share: Key share of the sender as a DID key.
        info: Application info that the sender used.

    Returns:
        :obj:`bytes`: Shared secret of 32 bytes.

    Raises:
        :class:`atproto_crypto.exceptions.DidKeyError`: The key share is not a DID key of a P-256 key,
            or the private key is not a P-256 key.
    """
    sender_key = _get_public_key_bytes(key_share)
    recipient_key = _get_public_key_bytes(private_key_to_did_key(private_key))

    return _derive_shared_secret(_exchange(private_key, sender_key), sender_key, recipient_key, info)
