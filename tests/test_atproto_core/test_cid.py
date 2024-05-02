from atproto_core.cid import CID, CIDType
from pydantic import BaseModel


def test_cid_decode_str() -> None:
    test_cid = 'bafyreihiurhwu7dp63wcu5x266pa7fiqm2zea7za4zfxz7hb3jhien7y5a'
    cid = CID.decode(test_cid)

    assert test_cid == str(cid)


def test_cid_decode_bytes() -> None:
    test_cid_str = 'bafyreibxym5cil3nzknuvhvtqexje2qr2weurpndoanv6lytwx3mhmh5uq'
    test_cid_bytes = (
        b'\x01q\x12 7\xc3:$/m\xca\x9bJ\x9e\xb3\x81.\x92j\x11\xd5\x89H\xbd\xa3p\x1b_/\x13\xb5\xf6\xc3\xb0\xfd\xa4'
    )
    cid = CID.decode(test_cid_bytes)

    assert test_cid_bytes == cid._raw_byte_form
    assert test_cid_str == cid.encode()


def test_cid_equal() -> None:
    test_cid = 'bafyreihiurhwu7dp63wcu5x266pa7fiqm2zea7za4zfxz7hb3jhien7y5a'

    cid1 = CID.decode(test_cid)
    cid2 = CID.decode(test_cid)

    assert cid1 == cid2
    assert test_cid == cid1
    assert test_cid == cid2

    assert hash(cid1) == hash(cid2)

    assert cid1 != b'blabla'


class _TestModel(BaseModel):
    cid: CIDType


def test_cid_type_str() -> None:
    test_cid = 'bafyreihiurhwu7dp63wcu5x266pa7fiqm2zea7za4zfxz7hb3jhien7y5a'

    model = _TestModel(cid=test_cid)

    assert isinstance(model.cid, CID)
    assert model.cid == CID.decode(test_cid)

    model_json = model.model_dump_json()
    assert model_json == f'{{"cid":"{test_cid}"}}'

    expected_json_schema = {
        'title': '_TestModel',
        'type': 'object',
        'properties': {
            'cid': {
                'title': 'Cid',
                'type': 'string',
            },
        },
        'required': ['cid'],
    }
    schema = model.model_json_schema()
    assert schema == expected_json_schema


def test_cid_type_bytes() -> None:
    test_cid = b'\x01q\x12 7\xc3:$/m\xca\x9bJ\x9e\xb3\x81.\x92j\x11\xd5\x89H\xbd\xa3p\x1b_/\x13\xb5\xf6\xc3\xb0\xfd\xa4'

    model = _TestModel(cid=test_cid)

    assert isinstance(model.cid, CID)
    assert model.cid == CID.decode(test_cid)

    model_json = model.model_dump_json()
    assert model_json == f'{{"cid":"{model.cid}"}}'
