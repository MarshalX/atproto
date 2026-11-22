import hashlib
import typing as t

import pytest
from atproto_crypto.lthash import LTHASH_STATE_SIZE, LtHash

_EMPTY_STATE = bytes(LTHASH_STATE_SIZE)

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/lthash.test.ts
_EMPTY_DIGEST = 'e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad'
_ONE_TWO_DIGEST = 'ae05cb6d224379d9710c290c8529945c5b0e0fde9ead30b9699057ce701c63e7'


def test_lthash_of_empty_set() -> None:
    lthash = LtHash()

    assert lthash.state == _EMPTY_STATE
    assert lthash.digest().hex() == _EMPTY_DIGEST


@pytest.mark.parametrize('elements', [('one', 'two'), ('two', 'one')])
def test_lthash_digest_does_not_depend_on_order(elements: t.Tuple[str, str]) -> None:
    lthash = LtHash()
    for element in elements:
        lthash.add(element)

    assert lthash.digest().hex() == _ONE_TWO_DIGEST
    assert lthash.digest() == hashlib.sha256(lthash.state).digest()


def test_lthash_remove_returns_to_previous_state() -> None:
    lthash = LtHash()
    lthash.add('one')
    state = lthash.state
    assert state != _EMPTY_STATE

    lthash.add('two')
    assert lthash.state != state

    lthash.remove('two')
    assert lthash.state == state

    lthash.remove('one')
    assert lthash.state == _EMPTY_STATE


def test_lthash_is_a_multiset() -> None:
    lthash = LtHash()
    lthash.add('one')
    lthash.add('one')
    assert lthash.state != _EMPTY_STATE

    once = LtHash()
    once.add('one')
    assert lthash != once

    lthash.remove('one')
    assert lthash == once


def test_lthash_distinguishes_elements() -> None:
    one = LtHash()
    one.add('one')
    two = LtHash()
    two.add('two')

    assert one != two
    assert one != one.state


def test_lthash_continues_from_state() -> None:
    lthash = LtHash()
    lthash.add('one')

    restored = LtHash(lthash.state)
    assert restored == lthash

    restored.add('two')
    assert restored.digest().hex() == _ONE_TWO_DIGEST


def test_lthash_accepts_element_of_any_length() -> None:
    element = 'a' * 5000

    lthash = LtHash()
    lthash.add(element)
    assert lthash.state != _EMPTY_STATE

    lthash.remove(element)
    assert lthash.state == _EMPTY_STATE


@pytest.mark.parametrize('size', [0, 32, LTHASH_STATE_SIZE - 1, LTHASH_STATE_SIZE + 1])
def test_lthash_rejects_state_of_wrong_length(size: int) -> None:
    with pytest.raises(ValueError, match='LtHash state must be 2048 bytes'):
        LtHash(bytes(size))
