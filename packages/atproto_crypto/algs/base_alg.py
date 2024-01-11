from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurve, EllipticCurvePublicKey

from atproto_crypto.exceptions import InvalidCompressedPubkeyError


class AlgBase:
    """Base class for all algorithms."""

    def __init__(self, curve: EllipticCurve) -> None:
        self.curve = curve

    def get_elliptic_curve_public_key(self, pubkey: bytes) -> EllipticCurvePublicKey:
        """Return the elliptic curve public key."""
        return EllipticCurvePublicKey.from_encoded_point(self.curve, pubkey)

    def compress_pubkey(self, pubkey: bytes) -> bytes:
        """Compress a public key."""
        return self.get_elliptic_curve_public_key(pubkey).public_bytes(
            encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint
        )

    def decompress_pubkey(self, pubkey: bytes) -> bytes:
        """Decompress a public key."""
        if len(pubkey) != 33:
            raise InvalidCompressedPubkeyError('Expected 33 byte compress pubkey')

        return self.get_elliptic_curve_public_key(pubkey).public_bytes(
            encoding=serialization.Encoding.X962, format=serialization.PublicFormat.UncompressedPoint
        )
