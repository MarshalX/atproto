import pytest
from atproto_core.cbor import decode_dag, decode_dag_multi
from atproto_core.exceptions import DAGCBORDecodingError


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
