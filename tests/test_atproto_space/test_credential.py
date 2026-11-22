import base64
import time

import pytest
from atproto_crypto.algs import P256
from atproto_crypto.did import parse_did_key, private_key_to_did_key
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from atproto_space import SpaceCredential
from atproto_space.exceptions import SpaceTokenError
from cryptography.hazmat.primitives.asymmetric import ec

from tests.test_atproto_space.token_builder import build_delegation_token, build_space_credential

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-space/src/space-credential.test.ts
_AUTHORITY = 'did:plc:authority'
_SPACE = 'at://did:plc:authority/space/com.example.group/test'
_ISSUED_AT = 1_700_000_000


def _generate_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def _build_credential(key: ec.EllipticCurvePrivateKey, expires_in: int = 600) -> str:
    return build_space_credential(
        _AUTHORITY, _SPACE, private_key_to_did_key(key), expires_in=expires_in, issued_at=_ISSUED_AT
    )


def test_parse_rejects_a_credential_bound_to_another_key() -> None:
    token = _build_credential(_generate_key())

    with pytest.raises(SpaceTokenError, match='not bound to the requested key') as exc_info:
        SpaceCredential.parse(token, _generate_key())

    assert exc_info.value.code == 'BadJwtCnf'


def test_parse_rejects_a_key_that_is_not_p256() -> None:
    token = _build_credential(_generate_key())

    with pytest.raises(UnsupportedKeyTypeError):
        SpaceCredential.parse(token, ec.generate_private_key(ec.SECP256K1()))


def test_parse_rejects_a_token_of_another_type() -> None:
    token = build_delegation_token('did:plc:alice', _SPACE, 'did:plc:authority#atproto_pds')

    with pytest.raises(SpaceTokenError) as exc_info:
        SpaceCredential.parse(token, _generate_key())

    assert exc_info.value.code == 'BadJwtType'


def test_credential_renews_a_minute_before_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    key = _generate_key()
    credential = SpaceCredential.parse(_build_credential(key), key)

    assert credential.renew_at == _ISSUED_AT + 600 - 60

    monkeypatch.setattr(time, 'time', lambda: _ISSUED_AT + 539)
    assert not credential.needs_renewal

    monkeypatch.setattr(time, 'time', lambda: _ISSUED_AT + 540)
    assert credential.needs_renewal


def test_short_lived_credential_renews_halfway_through() -> None:
    key = _generate_key()
    credential = SpaceCredential.parse(_build_credential(key, expires_in=10), key)

    assert credential.renew_at == _ISSUED_AT + 5


def test_credential_keeps_the_token_and_the_space_revision() -> None:
    key = _generate_key()
    token = _build_credential(key)

    assert SpaceCredential.parse(token, key).token == token
    assert SpaceCredential.parse(token, key).space_rev is None
    assert SpaceCredential.parse(token, key, space_rev='3kbcq3p7ad400').space_rev == '3kbcq3p7ad400'


def test_credential_reuses_the_signed_headers_of_an_audience() -> None:
    key = _generate_key()
    credential = SpaceCredential.parse(_build_credential(key), key)

    alice = credential.headers('did:plc:alice')
    bob = credential.headers('did:plc:bob')

    assert alice['authorization'] == f'Atproto-Space-Credential {credential.token}'
    assert alice['atproto-space-audience'] == 'did:plc:alice'
    assert bob['atproto-space-audience'] == 'did:plc:bob'
    assert credential.headers('did:plc:alice') == alice
    assert bob['signature'] != alice['signature']


def test_credential_headers_are_signed_with_the_bound_key() -> None:
    key = _generate_key()
    credential = SpaceCredential.parse(_build_credential(key), key)
    headers = credential.headers('did:plc:alice')

    signature_base = (
        f'"authorization": Atproto-Space-Credential {credential.token}\n'
        '"atproto-space-audience": did:plc:alice\n'
        '"@signature-params": ("authorization" "atproto-space-audience");tag="atproto-space-credential"'
    ).encode()
    signature = base64.b64decode(headers['signature'][len('sig=:') : -1], validate=True)

    assert P256().verify_signature(parse_did_key(private_key_to_did_key(key)).key_bytes, signature_base, signature)


def test_credential_headers_can_be_changed_by_the_caller() -> None:
    key = _generate_key()
    credential = SpaceCredential.parse(_build_credential(key), key)

    headers = credential.headers('did:plc:alice')
    headers['accept-signature'] = 'mac=("atproto-space-commit";sf)'

    assert 'accept-signature' not in credential.headers('did:plc:alice')
