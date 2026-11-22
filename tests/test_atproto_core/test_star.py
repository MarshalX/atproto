import json
import os
import typing as t

import pytest
from atproto_core.exceptions import InvalidStarError
from atproto_core.star import STAR

# Ref: https://github.com/bluesky-social/atproto/tree/b5fd12fa57b10cf068efa879812f558780f37109/packages/star/tests/interop
_FIXTURES_DIR_PATH = os.path.dirname(__file__)

_MINIMAL_STAR = bytes.fromhex('2A6C010008A16524747970656000')
# meta {'$type': 'abc'} of 11 bytes, then key b'key' and value b'value'
_STAR_WITH_PAIR = bytes.fromhex('2A6C01000BA16524747970656361626301036B65790576616C756500')


def _load_test_cases(filename: str) -> t.List[t.Dict[str, t.Any]]:
    with open(os.path.join(_FIXTURES_DIR_PATH, filename), encoding='UTF-8') as file:
        test_cases: t.List[t.Dict[str, t.Any]] = json.load(file)

    return test_cases


def test_star() -> None:
    star = STAR.from_bytes(_MINIMAL_STAR)

    assert star.meta == {'$type': ''}
    assert star.pairs == []


def test_star_with_pair() -> None:
    star = STAR.from_bytes(_STAR_WITH_PAIR)

    assert star.meta == {'$type': 'abc'}
    assert star.pairs == [(b'key', b'value')]


@pytest.mark.parametrize('test_case', _load_test_cases('valid-star-fixtures.json'), ids=lambda x: x['comment'])
def test_star_from_bytes(test_case: t.Dict[str, t.Any]) -> None:
    expected = test_case['decoded']

    star = STAR.from_bytes(bytes.fromhex(test_case['star_hex']))

    assert star.meta == expected['meta']
    assert star.pairs == [
        (bytes.fromhex(pair['key_hex']), bytes.fromhex(pair['value_hex'])) for pair in expected['pairs']
    ]


@pytest.mark.parametrize('test_case', _load_test_cases('invalid-star-fixtures.json'), ids=lambda x: x['comment'])
def test_star_from_bytes_with_invalid(test_case: t.Dict[str, t.Any]) -> None:
    with pytest.raises(InvalidStarError):
        STAR.from_bytes(bytes.fromhex(test_case['star_hex']))


def test_star_from_bytes_accepts_lengths_at_the_limits() -> None:
    star = STAR.from_bytes(_STAR_WITH_PAIR, max_meta_length=11, max_key_length=3, max_value_length=5)

    assert star.pairs == [(b'key', b'value')]


@pytest.mark.parametrize(
    'limits',
    [
        {'max_meta_length': 10},
        {'max_key_length': 2},
        {'max_value_length': 4},
    ],
)
def test_star_from_bytes_rejects_lengths_over_the_limits(limits: t.Dict[str, int]) -> None:
    with pytest.raises(InvalidStarError, match='exceeds limit'):
        STAR.from_bytes(_STAR_WITH_PAIR, **limits)


def test_star_from_bytes_checks_the_limit_before_reading_the_frame() -> None:
    # the value claims 2^56 bytes that are not there
    truncated = _STAR_WITH_PAIR[:21] + bytes.fromhex('808080808080808001')

    with pytest.raises(InvalidStarError, match='exceeds limit'):
        STAR.from_bytes(truncated, max_value_length=1024)

    with pytest.raises(InvalidStarError, match='Unexpected end'):
        STAR.from_bytes(truncated)


@pytest.mark.parametrize(
    'meta',
    [
        pytest.param('a2616e18016524747970656178', id='integer not in the shortest form'),
        pytest.param('a2616efa3fc000006524747970656178', id='float of 32 bits'),
        pytest.param('a1652474797065780178', id='length not in the shortest form'),
    ],
)
def test_star_from_bytes_rejects_metadata_that_is_not_canonical(meta: str) -> None:
    encoded = bytes.fromhex(meta)

    with pytest.raises(InvalidStarError, match='Metadata is not a map in canonical DAG-CBOR'):
        STAR.from_bytes(_MINIMAL_STAR[:4] + bytes([len(encoded)]) + encoded + b'\x00')


def test_star_from_bytes_accepts_float_of_64_bits_in_metadata() -> None:
    encoded = bytes.fromhex('a2616efb3ff80000000000006524747970656178')

    star = STAR.from_bytes(_MINIMAL_STAR[:4] + bytes([len(encoded)]) + encoded + b'\x00')

    assert star.meta == {'n': 1.5, '$type': 'x'}
