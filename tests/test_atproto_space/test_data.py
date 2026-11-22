import base64
import random
import typing as t

import libipld
import pytest
from atproto_core.cbor import decode_dag
from atproto_core.cid import CID
from atproto_space._data import (
    DAG_CBOR_CODEC,
    RAW_CODEC,
    encode_json_value,
    get_blob_cid,
    get_record_cid,
    is_sha256_cid,
    json_to_ipld,
)

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/mac.test.ts#L22-L28
_HELLO_CID = 'bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244'
_HELLO_CID_BYTES = bytes.fromhex('017112206428f02304b8db8cb107c89336481f0fead728bf374ca80168d2c71938cefae7')
_WORLD_CID = 'bafyreidpw4cbv6gr4ukh33z23pvvrpr3wi4gnpmi4doamlsl3sa4rgri2a'

_HELLO_CID_BASE36 = 'k2jvsl7vxk6iz8njefrkq17l9u8s5z1cyfb3tn1iym9649ognjyv6oyv'
_HELLO_CID_BASE58 = 'zdpuAsARTWMKk1MSVTHzd5MGqKnJpUcpyFv12cXakdVgXGKN6'

# CID of the raw bytes b'hello'
_BLOB_CID = 'bafkreibm6jg3ux5qumhcn2b3flc3tyu6dmlb4xa7u5bf44yegnrjhc4yeq'

_V0_CID = 'QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG'
_V0_CID_BYTES = bytes.fromhex('12209d6c2be50f706953479ab9df2ce3edca90b68053c00b3004b7f0accbe1e8eedf')

# digest of SHA-512
_SHA512_CID = (
    'bafyrgqe3ohjcjplc6n4f3fwunlj6upltggn7xqujbsvnvyw764srszz4u4rshq6ztos4chl4plgg4ffyyxnayrtdi5oc4xb2332g645433aeg'
)
_SHA512_CID_BYTES = bytes.fromhex(
    '017113409b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7'
    '2323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043'
)

_AMBIGUOUS_BYTES = b'\x01' * 32
_LINK = {'$link': _HELLO_CID}

_INTEGERS = (0, 23, 24, 255, 256, 65535, 65536, 2**32 - 1, 2**32, 2**53, -1, -24, -25, -256, -257, -(2**53))


def _random_value(rnd: random.Random, depth: int = 0) -> t.Any:
    kind = rnd.randrange(7 if depth < 4 else 5)
    if kind == 0:
        return rnd.choice([None, True, False])
    if kind == 1:
        return rnd.choice(_INTEGERS)
    if kind in (2, 3):
        return ''.join(rnd.choice('abcé日本$ ') for _ in range(rnd.randrange(40)))
    if kind == 4:
        return _LINK
    if kind == 5:
        return [_random_value(rnd, depth + 1) for _ in range(rnd.randrange(5))]

    return {
        ''.join(rnd.choice('abc$Zé') for _ in range(rnd.randrange(1, 30))): _random_value(rnd, depth + 1)
        for _ in range(rnd.randrange(6))
    }


def _replace_links(value: t.Any) -> t.Any:
    if value == _LINK:
        return CID(_HELLO_CID)
    if isinstance(value, list):
        return [_replace_links(item) for item in t.cast('t.List[t.Any]', value)]
    if isinstance(value, dict):
        return {key: _replace_links(item) for key, item in t.cast('t.Dict[str, t.Any]', value).items()}

    return value


def _encode_base64(data: bytes, padded: bool) -> str:
    encoded = base64.b64encode(data).decode('ascii')
    return encoded if padded else encoded.rstrip('=')


def test_encode_json_value() -> None:
    assert encode_json_value({'text': 'hello'}).hex() == 'a164746578746568656c6c6f'


def test_encode_json_value_matches_libipld() -> None:
    rnd = random.Random(7)  # noqa: S311

    for _ in range(3000):
        value = {'$type': 'com.example.record', 'value': _random_value(rnd)}
        assert encode_json_value(value) == libipld.encode_dag_cbor(_replace_links(value))


@pytest.mark.parametrize('padded', [True, False])
def test_encode_json_value_keeps_bytes_a_byte_string(padded: bool) -> None:
    value = {'d': {'$bytes': _encode_base64(_AMBIGUOUS_BYTES, padded)}}

    assert encode_json_value(value).hex() == 'a161645820' + '01' * 32


def test_encode_json_value_encodes_link() -> None:
    assert encode_json_value({'l': _LINK}).hex() == 'a1616cd82a582500' + _HELLO_CID_BYTES.hex()


def test_encode_json_value_encodes_blob_ref() -> None:
    blob = {'$type': 'blob', 'ref': _LINK, 'mimeType': 'image/png', 'size': 3}

    assert encode_json_value(blob) == libipld.encode_dag_cbor({**blob, 'ref': CID(_HELLO_CID)})


@pytest.mark.parametrize(
    'value',
    [
        {'$link': 'nope'},
        {'$link': ''},
        {'$link': 1},
        {'$link': _HELLO_CID, 'extra': 1},
        {'$bytes': '!!!!'},
        {'$bytes': 'A'},
        {'$bytes': 'é'},
        {'$bytes': 1},
        {'$bytes': 'AQID', 'extra': 1},
    ],
)
def test_encode_json_value_keeps_malformed_link_and_bytes_a_map(value: t.Dict[str, t.Any]) -> None:
    assert encode_json_value({'v': value}) == libipld.encode_dag_cbor({'v': value})


@pytest.mark.parametrize(
    ('link', 'cid'),
    [
        (_HELLO_CID, _HELLO_CID_BYTES),
        (f'{_HELLO_CID}=', _HELLO_CID_BYTES),
        (_HELLO_CID_BASE36, _HELLO_CID_BYTES),
        (_HELLO_CID_BASE58, _HELLO_CID_BYTES),
        (_V0_CID, _V0_CID_BYTES),
        (_SHA512_CID, _SHA512_CID_BYTES),
        # 128 characters
        (f'{_SHA512_CID}{"=" * 18}', _SHA512_CID_BYTES),
    ],
)
def test_encode_json_value_reads_link_in_the_forms_that_hosts_read(link: str, cid: bytes) -> None:
    assert encode_json_value({'l': {'$link': link}}).hex() == f'a1616cd82a58{len(cid) + 1:02x}00{cid.hex()}'


@pytest.mark.parametrize(
    'link',
    [
        _HELLO_CID.upper(),
        f'b{_HELLO_CID[1:].upper()}',
        _HELLO_CID_BASE36.upper(),
        f'k{_HELLO_CID_BASE36[1:].upper()}',
        # base16, base64 and base64url
        f'f{_HELLO_CID_BYTES.hex()}',
        f'F{_HELLO_CID_BYTES.hex().upper()}',
        'mAXESIGQo8CMEuNuMsQfIkzZIHw/q1yi/N0yoAWjSxxk4zvrn',
        'uAXESIGQo8CMEuNuMsQfIkzZIHw_q1yi_N0yoAWjSxxk4zvrn',
        # CIDv0 with a multibase prefix
        f'z{_V0_CID}',
        'bciqj23bl4uhxa2kti6nltxzm4pw4vefwqbj4aczqas37blgl4huo5xy',
        # a byte after the CID
        f'{_HELLO_CID}aa',
        f'/ipfs/{_HELLO_CID}',
        f'{_HELLO_CID}\n',
        f'{_HELLO_CID_BASE58}=',
        # 129 characters
        f'{_SHA512_CID}{"=" * 19}',
    ],
)
def test_encode_json_value_keeps_link_in_the_forms_that_hosts_do_not_read_a_map(link: str) -> None:
    text = link.encode()

    assert encode_json_value({'l': {'$link': link}}).hex() == f'a1616ca165246c696e6b78{len(text):02x}{text.hex()}'


@pytest.mark.parametrize(('value', 'expected'), [(1.0, 1), (-0.0, 0), (1e3, 1000), (-(2.0**53) + 1, -(2**53) + 1)])
def test_encode_json_value_takes_whole_float_as_integer(value: float, expected: int) -> None:
    assert encode_json_value({'n': [value]}) == encode_json_value({'n': [expected]})


@pytest.mark.parametrize(
    'value',
    [1.5, float('nan'), float('inf'), 2.0**53, 2**64, -(2**64) - 1, object(), {1: 'a'}, '\ud800'],
)
def test_encode_json_value_rejects_value_outside_data_model(value: t.Any) -> None:
    with pytest.raises(ValueError, match=r'safe integer|no DAG-CBOR form'):
        encode_json_value({'v': {'nested': [value]}})


def test_encode_json_value_rejects_value_that_is_nested_too_deep() -> None:
    value: t.List[t.Any] = []
    for _ in range(1000):
        value = [value]

    with pytest.raises(ValueError, match='no DAG-CBOR form'):
        encode_json_value({'v': value})


def test_json_to_ipld() -> None:
    value = {
        '$type': 'com.example.record',
        'items': [1, -1, 'a', None, True, 2.0, {'b': {'$bytes': 'AQI'}}],
        'link': _LINK,
        'data': {'$bytes': _encode_base64(_AMBIGUOUS_BYTES, padded=False)},
    }

    ipld = json_to_ipld(value)

    assert ipld == {
        '$type': 'com.example.record',
        'items': [1, -1, 'a', None, True, 2, {'b': b'\x01\x02'}],
        'link': CID(_HELLO_CID),
        'data': _AMBIGUOUS_BYTES,
    }
    assert ipld == decode_dag(encode_json_value(value))


@pytest.mark.parametrize('value', [[1], 'text', 1, None, _LINK, {'v': 1.5}])
def test_json_to_ipld_rejects_value_that_is_not_a_map_of_the_data_model(value: t.Any) -> None:
    with pytest.raises(ValueError, match=r'safe integer|not a DAG-CBOR map'):
        json_to_ipld(value)


@pytest.mark.parametrize(('record', 'cid'), [({'text': 'hello'}, _HELLO_CID), ({'text': 'world'}, _WORLD_CID)])
def test_get_record_cid(record: t.Dict[str, t.Any], cid: str) -> None:
    assert get_record_cid(encode_json_value(record)) == cid


def test_get_blob_cid() -> None:
    assert get_blob_cid(b'hello') == _BLOB_CID


def test_is_sha256_cid() -> None:
    assert is_sha256_cid(_HELLO_CID, DAG_CBOR_CODEC)
    assert is_sha256_cid(_BLOB_CID, RAW_CODEC)


@pytest.mark.parametrize(
    ('cid', 'codec'),
    [
        (_HELLO_CID, RAW_CODEC),
        (_BLOB_CID, DAG_CBOR_CODEC),
        # the same CID in upper case, in base58btc and in base16
        (_HELLO_CID.upper(), DAG_CBOR_CODEC),
        (_HELLO_CID_BASE58, DAG_CBOR_CODEC),
        (f'f{_HELLO_CID_BYTES.hex()}', DAG_CBOR_CODEC),
        (_V0_CID, 0x70),
        (_SHA512_CID, DAG_CBOR_CODEC),
        (f'{_HELLO_CID}\n', DAG_CBOR_CODEC),
        (f'{_HELLO_CID}{"a" * 128}', DAG_CBOR_CODEC),
        ('nope', DAG_CBOR_CODEC),
        ('', DAG_CBOR_CODEC),
    ],
)
def test_is_sha256_cid_rejects_other_cid(cid: str, codec: int) -> None:
    assert not is_sha256_cid(cid, codec)


def test_is_sha256_cid_does_not_decode_string_longer_than_any_cid(monkeypatch: pytest.MonkeyPatch) -> None:
    decoded: t.List[str] = []
    monkeypatch.setattr(CID, 'decode', decoded.append)

    assert not is_sha256_cid('z' * 129, DAG_CBOR_CODEC)
    assert not is_sha256_cid('z' * 128, DAG_CBOR_CODEC)
    assert decoded == ['z' * 128]
