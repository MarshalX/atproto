import typing as t

import pytest
from atproto_core.did_doc import DidDocument, is_valid_did_doc
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from atproto_crypto.kem import encapsulate

_DID = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'

# Ref: https://github.com/bluesky-social/indigo/blob/066d55aa678f62c70ada9e7c2b6ee5026283cf2a/atproto/identity/testdata/space_doc.json
_SPACE_DID = 'did:plc:735r43lcgemuv2woqpvx3lso'
_SPACE_DOC = {
    'id': _SPACE_DID,
    'alsoKnownAs': ['at://space.example.com'],
    'verificationMethod': [
        {
            'id': f'{_SPACE_DID}#atproto',
            'type': 'Multikey',
            'controller': _SPACE_DID,
            'publicKeyMultibase': 'zQ3shaMhbTC3fbTqdq2yuUs8aW2a7Hh6AiSxmrj8GA6z4z18K',
        },
        {
            'id': f'{_SPACE_DID}#atproto_kem',
            'type': 'Multikey',
            'controller': _SPACE_DID,
            'publicKeyMultibase': 'zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg',
        },
    ],
    'service': [
        {'id': '#atproto_pds', 'type': 'AtprotoPersonalDataServer', 'serviceEndpoint': 'https://pds.example.com'}
    ],
}


def _doc_with_key(key_type: str, public_key_multibase: str, key_id: str = '#atproto_kem') -> DidDocument:
    key = {'id': key_id, 'type': key_type, 'controller': _DID, 'publicKeyMultibase': public_key_multibase}
    return DidDocument.from_dict({'id': _DID, 'verificationMethod': [key]})


class _DocWrapper:
    def to_dict(self) -> t.Dict[str, t.Any]:
        return {'id': _DID}


def test_did_doc_from_dict() -> None:
    assert DidDocument.from_dict({'id': _DID}).id == _DID
    assert DidDocument.from_dict(_DocWrapper()).id == _DID


def test_is_valid_did_doc() -> None:
    assert is_valid_did_doc({'id': _DID})
    assert is_valid_did_doc(_DocWrapper())
    assert not is_valid_did_doc({})
    assert not is_valid_did_doc([_DID])


def test_get_kem_key() -> None:
    did_doc = DidDocument.from_dict(_SPACE_DOC)

    assert did_doc.get_kem_key() == 'did:key:zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg'
    assert did_doc.get_did_key() == 'did:key:zQ3shaMhbTC3fbTqdq2yuUs8aW2a7Hh6AiSxmrj8GA6z4z18K'


def test_get_kem_key_with_relative_id() -> None:
    did_doc = _doc_with_key('Multikey', 'zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg')

    assert did_doc.get_kem_key() == 'did:key:zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg'


def test_get_kem_key_with_legacy_p256_type() -> None:
    did_doc = _doc_with_key('EcdsaSecp256r1VerificationKey2019', 'zxdM8dSstjrpZaRUwBmDvjGXweKuEMVN95A9oJBFjkWMh')

    assert did_doc.get_kem_key() == 'did:key:zDnaembgSGUhZULN2Caob4HLJPaxBh92N7rtH21TErzqf8HQo'


def test_get_kem_key_without_kem_key() -> None:
    did_doc = _doc_with_key('Multikey', 'zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg', key_id='#atproto')

    assert did_doc.get_kem_key() is None
    assert DidDocument.from_dict({'id': _DID}).get_kem_key() is None


def test_get_kem_key_with_legacy_secp256k1_type() -> None:
    did_doc = _doc_with_key(
        'EcdsaSecp256k1VerificationKey2019',
        'zQYEBzXeuTM9UR3rfvNag6L3RNAs5pQZyYPsomTsgQhsxLdEgCrPTLgFna8yqCnxPpNT7DBk6Ym3dgPKNu86vt9GR',
    )

    assert did_doc.get_kem_key() is None


def test_get_kem_key_of_another_did() -> None:
    did_doc = _doc_with_key(
        'Multikey', 'zDnaeg3Q1594Zy2wxzm5g466bepmyYVnqFD57rRX7PAcmCccg', key_id=f'{_SPACE_DID}#atproto_kem'
    )

    assert did_doc.get_kem_key() is None


def test_get_kem_key_does_not_check_the_curve() -> None:
    did_doc = _doc_with_key('Multikey', 'zQ3shaMhbTC3fbTqdq2yuUs8aW2a7Hh6AiSxmrj8GA6z4z18K')

    kem_key = did_doc.get_kem_key()
    assert kem_key == 'did:key:zQ3shaMhbTC3fbTqdq2yuUs8aW2a7Hh6AiSxmrj8GA6z4z18K'

    with pytest.raises(UnsupportedKeyTypeError):
        encapsulate(kem_key, b'info')
