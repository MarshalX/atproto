import typing as t

from atproto_core.did_doc import DidDocument, is_valid_did_doc

_DID = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'


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
