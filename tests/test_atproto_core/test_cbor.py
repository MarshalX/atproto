import typing as t

import pytest
from atproto_core.cbor import decode_dag, decode_dag_multi, encode_dag
from atproto_core.cid import CID
from atproto_core.exceptions import DAGCBORDecodingError, DAGCBOREncodingError

_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
_CID_BYTES = bytes.fromhex('017112206428f02304b8db8cb107c89336481f0fead728bf374ca80168d2c71938cefae7')
_CID_V0_BYTES = bytes.fromhex('12209d6c2be50f706953479ab9df2ce3edca90b68053c00b3004b7f0accbe1e8eedf')

_NOT_CANONICAL = [
    pytest.param('a161611801', id='integer'),
    pytest.param('a161611b0000000000000100', id='integer of 64 bits'),
    pytest.param('a161613800', id='negative integer'),
    pytest.param('a16161780161', id='length of a string'),
    pytest.param('a16161580161', id='length of bytes'),
    pytest.param('a178016101', id='length of a key'),
    pytest.param('a16161980101', id='length of an array'),
    pytest.param('b801616101', id='length of a map'),
    pytest.param('a16161d9002a582500' + _CID_BYTES.hex(), id='tag of a link'),
    pytest.param('a16161d82a59002500' + _CID_BYTES.hex(), id='length of a link'),
    pytest.param('a16161fa3fc00000', id='float of 32 bits'),
]


def test_decode_dag() -> None:
    assert decode_dag(b'\xa1\x61a\x01') == {'a': 1}


def test_decode_dag_multi() -> None:
    assert decode_dag_multi(b'\xa1\x61a\x01\xa0') == [{'a': 1}, {}]


@pytest.mark.parametrize('data', [b'\xa0\x00', b'\xff\xff'])
def test_decode_dag_rejects_malformed_data(data: bytes) -> None:
    with pytest.raises(DAGCBORDecodingError):
        decode_dag(data)


@pytest.mark.parametrize('data', [b'\x01', b'\x80'])
def test_decode_dag_rejects_non_map(data: bytes) -> None:
    with pytest.raises(DAGCBORDecodingError):
        decode_dag(data)


@pytest.mark.parametrize('data', [b'\xff\xff', b'\xa0\xff', b'\xa0\xa1'])
def test_decode_dag_multi_rejects_malformed_data(data: bytes) -> None:
    with pytest.raises(DAGCBORDecodingError):
        decode_dag_multi(data)


@pytest.mark.parametrize(
    ('data', 'cid'),
    [('a16161d82a582500' + _CID_BYTES.hex(), _CID_BYTES), ('a16161d82a582300' + _CID_V0_BYTES.hex(), _CID_V0_BYTES)],
)
def test_decode_dag_decodes_link_to_cid(data: str, cid: bytes) -> None:
    assert decode_dag(bytes.fromhex(data), canonical=True) == {'a': CID(cid)}


@pytest.mark.parametrize('data', _NOT_CANONICAL)
def test_decode_dag_canonical_rejects_head_that_is_not_the_shortest(data: str) -> None:
    encoded = bytes.fromhex(data)

    assert decode_dag(encoded)
    with pytest.raises(DAGCBORDecodingError):
        decode_dag(encoded, canonical=True)


@pytest.mark.parametrize('data', _NOT_CANONICAL)
def test_decode_dag_multi_canonical_rejects_head_that_is_not_the_shortest(data: str) -> None:
    encoded = b'\xa0' + bytes.fromhex(data)

    assert decode_dag_multi(encoded)
    with pytest.raises(DAGCBORDecodingError):
        decode_dag_multi(encoded, canonical=True)


@pytest.mark.parametrize(
    'data',
    [
        pytest.param('a16161d82a582600' + _CID_BYTES.hex() + '01', id='one byte'),
        pytest.param('a16161d82a582700' + _CID_BYTES.hex() + '0102', id='two bytes'),
        pytest.param('a16161d82a582400' + _CID_V0_BYTES.hex() + '01', id='CIDv0'),
        pytest.param('a26161d82a582600' + _CID_BYTES.hex() + '01616201', id='before another item'),
    ],
)
def test_decode_dag_rejects_bytes_after_the_cid_of_a_link(data: str) -> None:
    with pytest.raises(DAGCBORDecodingError):
        decode_dag(bytes.fromhex(data))


def test_encode_dag() -> None:
    assert encode_dag({'text': 'hello'}).hex() == 'a164746578746568656c6c6f'


def test_encode_dag_keeps_bytes_a_byte_string() -> None:
    assert encode_dag({'d': _CID_BYTES}).hex() == 'a161645824' + _CID_BYTES.hex()


@pytest.mark.parametrize(
    ('cid', 'expected'),
    [
        (CID(_CID), 'd82a582500' + _CID_BYTES.hex()),
        (CID(_CID_BYTES), 'd82a582500' + _CID_BYTES.hex()),
        (CID('QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG'), 'd82a582300' + _CID_V0_BYTES.hex()),
    ],
)
def test_encode_dag_encodes_cid_as_link(cid: CID, expected: str) -> None:
    assert encode_dag(cid).hex() == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ((1, 2), '820102'),
        # DAG-CBOR has no negative zero
        (-0.0, 'fb0000000000000000'),
        (1.5, 'fb3ff8000000000000'),
    ],
)
def test_encode_dag_encodes_value(value: t.Any, expected: str) -> None:
    assert encode_dag(value).hex() == expected


def test_encode_dag_sorts_keys_by_length_then_bytes() -> None:
    value = {'bb': 1, 'c': 2, 'a' * 24: 3, 'é': 4, 'b' * 23: 5, 'a': 6, 'B': 7}

    assert list(decode_dag(encode_dag(value), canonical=True)) == ['B', 'a', 'c', 'bb', 'é', 'b' * 23, 'a' * 24]


def test_encode_dag_roundtrip() -> None:
    value = {
        '$type': 'com.example.record',
        'items': [1, -1, 'a', None, True, {'b': b'\x01\x02'}],
        'link': CID(_CID),
    }

    assert decode_dag(encode_dag(value), canonical=True) == value


@pytest.mark.parametrize(
    'value',
    [
        float('nan'),
        float('inf'),
        2**64,
        -(2**64) - 1,
        {1: 'a'},
        {'a': {1: 'a'}},
        {'a': {'b'}},
        [object()],
        bytearray(b'a'),
        '\ud800',
    ],
)
def test_encode_dag_rejects_unsupported_value(value: t.Any) -> None:
    with pytest.raises(DAGCBOREncodingError):
        encode_dag(value)
