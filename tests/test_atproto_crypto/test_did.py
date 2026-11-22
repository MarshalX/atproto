import pytest
from atproto_crypto.consts import P256_JWT_ALG, SECP256K1_JWT_ALG
from atproto_crypto.did import (
    Multikey,
    format_did_key,
    format_multikey,
    get_did_key,
    get_multikey_alg,
    parse_did_key,
    private_key_to_did_key,
)
from atproto_crypto.exceptions import IncorrectMultikeyPrefixError, UnsupportedKeyTypeError
from cryptography.hazmat.primitives.asymmetric import ec


def test_get_multikey_alg_secp256k1() -> None:
    pubkey_multibase = 'zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'
    expected_jwt_alg = SECP256K1_JWT_ALG

    jwt_alg = get_multikey_alg(pubkey_multibase)
    assert jwt_alg == expected_jwt_alg


def test_get_multikey_alg_p256() -> None:
    pubkey_multibase = 'zDnaembgSGUhZULN2Caob4HLJPaxBh92N7rtH21TErzqf8HQo'
    expected_jwt_alg = P256_JWT_ALG

    jwt_alg = get_multikey_alg(pubkey_multibase)
    assert jwt_alg == expected_jwt_alg


def test_get_multikey_alg_unsupported_key_type() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        get_multikey_alg('zxdM8dSstjrpZaRUwBmDvjGXweKuEMVN95A9oJBFjkWMh')


def test_get_multikey_alg_wrong_multibase() -> None:
    with pytest.raises(IncorrectMultikeyPrefixError):
        get_multikey_alg('uVGhlIEFUIFByb3RvY29sIFNESyBmb3IgUHl0aG9uIGJ5IE1hcnNoYWw')


def test_multikey_p256_compress_decompress() -> None:
    expected_pubkey_multibase = 'zDnaembgSGUhZULN2Caob4HLJPaxBh92N7rtH21TErzqf8HQo'

    multikey = Multikey.from_str(expected_pubkey_multibase)
    assert multikey.jwt_alg == P256_JWT_ALG

    did_key = format_multikey(multikey.jwt_alg, multikey.key_bytes)
    did_key2 = multikey.to_str()
    assert did_key == expected_pubkey_multibase
    assert did_key2 == expected_pubkey_multibase


def test_multikey_secp256k1_compress_decompress() -> None:
    expected_pubkey_multibase = 'zQ3shc6V2kvUxn7hNmPy9JMToKT7u2NH27SnKNxGL1GcBcS4j'

    multikey = Multikey.from_str(expected_pubkey_multibase)
    assert multikey.jwt_alg == SECP256K1_JWT_ALG

    did_key = format_multikey(multikey.jwt_alg, multikey.key_bytes)
    assert did_key == expected_pubkey_multibase


def test_parse_multikey_unsupported_key_type() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        Multikey.from_str('zxdM8dSstjrpZaRUwBmDvjGXweKuEMVN95A9oJBFjkWMh')


def test_parse_multikey_alg_wrong_multibase() -> None:
    with pytest.raises(IncorrectMultikeyPrefixError):
        Multikey.from_str('uVGhlIEFUIFByb3RvY29sIFNESyBmb3IgUHl0aG9uIGJ5IE1hcnNoYWw')


def test_get_did_key_with_secp256k1() -> None:
    key_type = 'EcdsaSecp256k1VerificationKey2019'
    pubkey_multibase = 'zQYEBzXeuTM9UR3rfvNag6L3RNAs5pQZyYPsomTsgQhsxLdEgCrPTLgFna8yqCnxPpNT7DBk6Ym3dgPKNu86vt9GR'
    expected_did_key = 'did:key:zQ3shXjHeiBuRCKmM36cuYnm7YEMzhGnCmCyW92sRJ9pribSF'

    did_key = get_did_key(key_type, pubkey_multibase)
    assert did_key == expected_did_key


def test_get_did_key_with_p256() -> None:
    key_type = 'EcdsaSecp256r1VerificationKey2019'
    pubkey_multibase = 'zxdM8dSstjrpZaRUwBmDvjGXweKuEMVN95A9oJBFjkWMh'
    expected_did_key = 'did:key:zDnaembgSGUhZULN2Caob4HLJPaxBh92N7rtH21TErzqf8HQo'

    did_key = get_did_key(key_type, pubkey_multibase)
    assert did_key == expected_did_key


def test_get_did_key_with_multikey() -> None:
    key_type = 'Multikey'
    pubkey_multibase = 'zQ3shXjHeiBuRCKmM36cuYnm7YEMzhGnCmCyW92sRJ9pribSF'
    expected_did_key = 'did:key:zQ3shXjHeiBuRCKmM36cuYnm7YEMzhGnCmCyW92sRJ9pribSF'

    did_key = get_did_key(key_type, pubkey_multibase)
    assert did_key == expected_did_key


def test_format_did_key_unsupported_key_type() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        format_did_key('blabla', b'')


def test_private_key_to_did_key() -> None:
    # the public key of the private value 3
    expected_key_bytes = bytes.fromhex(
        '045ecbe4d1a6330a44c8f7ef951d4bf165e6c6b721efada985fb41661bc6e7fd6c'
        '8734640c4998ff7e374b06ce1a64a2ecd82ab036384fb83d9a79b127a27d5032'
    )

    did_key = private_key_to_did_key(ec.derive_private_key(3, ec.SECP256R1()))
    assert did_key == format_did_key(P256_JWT_ALG, expected_key_bytes)

    multikey = parse_did_key(did_key)
    assert multikey.jwt_alg == P256_JWT_ALG
    assert multikey.key_bytes == expected_key_bytes


def test_private_key_to_did_key_unsupported_key_type() -> None:
    with pytest.raises(UnsupportedKeyTypeError):
        private_key_to_did_key(ec.generate_private_key(ec.SECP256K1()))
