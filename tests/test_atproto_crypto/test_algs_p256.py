import pytest
from atproto_crypto.algs import P256
from atproto_crypto.exceptions import InvalidCompressedPubkeyError


def test_decompress_pubkey_invalid_compression() -> None:
    with pytest.raises(InvalidCompressedPubkeyError):
        P256().decompress_pubkey('blabla')
