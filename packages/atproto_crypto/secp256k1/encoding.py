from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import SECP256K1, EllipticCurvePublicKey


def compress_public_key(pubkey: bytes) -> bytes:
    public_key = EllipticCurvePublicKey.from_encoded_point(SECP256K1(), pubkey)
    return public_key.public_bytes(
        encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint
    )


def decompress_public_key(pubkey: bytes) -> bytes:
    if len(pubkey) != 33:
        raise ValueError('Expected 33 byte compress pubkey')

    public_key = EllipticCurvePublicKey.from_encoded_point(SECP256K1(), pubkey)
    return public_key.public_bytes(
        encoding=serialization.Encoding.X962, format=serialization.PublicFormat.UncompressedPoint
    )
