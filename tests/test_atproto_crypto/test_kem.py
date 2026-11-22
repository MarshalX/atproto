import pytest
from atproto_crypto.consts import P256_JWT_ALG
from atproto_crypto.did import format_did_key, private_key_to_did_key
from atproto_crypto.exceptions import IncorrectDidKeyPrefixError, IncorrectMultikeyPrefixError, UnsupportedKeyTypeError
from atproto_crypto.kem import decapsulate, encapsulate
from atproto_crypto.multibase import bytes_to_multibase
from cryptography.hazmat.primitives.asymmetric import ec

_INFO = b'atproto-mac'

_SECP256K1_DID_KEY = 'did:key:zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'

_P256_PREFIX = b'\x80\x24'
# DID keys with the prefix of P-256 that hold no P-256 key
_MALFORMED_DID_KEYS = [
    pytest.param(_P256_PREFIX + b'\x02' + b'\xff' * 32, id='point off the curve'),
    pytest.param(_P256_PREFIX + b'\x04' + b'\xff' * 64, id='point that is not compressed'),
    pytest.param(_P256_PREFIX, id='no point'),
]


def _private_key(private_value: int) -> ec.EllipticCurvePrivateKey:
    return ec.derive_private_key(private_value, ec.SECP256R1())


def test_decapsulate_matches_hpke_secret_export() -> None:
    # Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/kem.test.ts#L60-L80
    key_share = bytes.fromhex(
        '04d804370b7e24b94749eb1dc8df6d4d4a5d75f9effad01739ebcad5c54a40d57a'
        'aa8b4190fc124dbde2e4f1e1d1b012a3bc4038157dc29b55533a932306d8d38d'
    )
    private_key = _private_key(0x62C3868357A464F8461D03AA0182C7CEBCDE841036AEA7230DDC7339F1088346)
    expected = '2060e0558d1b34c10086bc137f849bb79ba59fcdc30544418e35c9cd301f0d0d'

    shared_secret = decapsulate(private_key, format_did_key(P256_JWT_ALG, key_share), _INFO)
    assert shared_secret.hex() == expected


def test_decapsulate_binds_secret_to_both_keys() -> None:
    # Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/spaces/mac_test.go#L15-L34
    sender = _private_key(3)
    recipient = _private_key(7)
    expected = '6d5583f6c99086921a36ba07358a13195fd4a1da7beb30eff853f05691108baf'

    shared_secret = decapsulate(recipient, private_key_to_did_key(sender), _INFO)
    assert shared_secret.hex() == expected

    assert decapsulate(sender, private_key_to_did_key(recipient), _INFO) != shared_secret


def test_decapsulate_binds_secret_to_info() -> None:
    sender = _private_key(3)
    recipient = _private_key(7)

    assert decapsulate(recipient, private_key_to_did_key(sender), b'info') != decapsulate(
        recipient, private_key_to_did_key(sender), _INFO
    )


def test_encapsulate_roundtrip() -> None:
    recipient = ec.generate_private_key(ec.SECP256R1())

    encapsulation = encapsulate(private_key_to_did_key(recipient), _INFO)

    assert len(encapsulation.shared_secret) == 32
    assert decapsulate(recipient, encapsulation.key_share, _INFO) == encapsulation.shared_secret
    assert decapsulate(_private_key(7), encapsulation.key_share, _INFO) != encapsulation.shared_secret


def test_encapsulate_uses_new_key_share_each_time() -> None:
    recipient = private_key_to_did_key(_private_key(7))

    first = encapsulate(recipient, _INFO)
    second = encapsulate(recipient, _INFO)

    assert first.key_share != second.key_share
    assert first.shared_secret != second.shared_secret


def test_encapsulation_repr_hides_shared_secret() -> None:
    encapsulation = encapsulate(private_key_to_did_key(_private_key(7)), _INFO)

    assert encapsulation.key_share in repr(encapsulation)
    assert 'shared_secret' not in repr(encapsulation)


def test_encapsulate_rejects_secp256k1_key() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        encapsulate(_SECP256K1_DID_KEY, _INFO)


@pytest.mark.parametrize('key', _MALFORMED_DID_KEYS)
def test_encapsulate_rejects_malformed_key(key: bytes) -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        encapsulate(f'did:key:{bytes_to_multibase("z", key)}', _INFO)


def test_encapsulate_rejects_key_that_is_not_multibase() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        encapsulate('did:key:z!!!', _INFO)


def test_encapsulate_rejects_key_without_did_key_prefix() -> None:
    with pytest.raises(IncorrectDidKeyPrefixError):
        encapsulate('zDnaembgSGUhZULN2Caob4HLJPaxBh92N7rtH21TErzqf8HQo', _INFO)


def test_decapsulate_rejects_secp256k1_key_share() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        decapsulate(_private_key(7), _SECP256K1_DID_KEY, _INFO)


@pytest.mark.parametrize('key', _MALFORMED_DID_KEYS)
def test_decapsulate_rejects_malformed_key_share(key: bytes) -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        decapsulate(_private_key(7), f'did:key:{bytes_to_multibase("z", key)}', _INFO)


def test_decapsulate_rejects_invalid_key_share() -> None:
    with pytest.raises(IncorrectMultikeyPrefixError):
        decapsulate(_private_key(7), 'did:key:nope', _INFO)


def test_decapsulate_rejects_secp256k1_private_key() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        decapsulate(ec.generate_private_key(ec.SECP256K1()), private_key_to_did_key(_private_key(3)), _INFO)
