import typing as t
from pathlib import Path

import pytest
from atproto_core.exceptions import InvalidAtUriError
from atproto_core.uri import SpaceRef
from atproto_lexicon.models import LexiconDoc
from atproto_lexicon.parser import lexicon_parse_file
from atproto_space import SpaceType

_LEXICONS = Path(__file__).parent.parent / 'fixtures' / 'space_lexicons'

_DID = 'did:example:123'
_GROUP = 'com.example.group'


def _parse_lexicon(name: str) -> LexiconDoc:
    lexicon = lexicon_parse_file(_LEXICONS / name)
    assert lexicon is not None

    return lexicon


def test_from_lexicon() -> None:
    space_type = SpaceType.from_lexicon(_parse_lexicon('com.example.space.json'))

    assert space_type == SpaceType('com.example.space', 'any', ('com.example.spaceRecord',))


def test_from_lexicon_rejects_a_lexicon_of_another_definition() -> None:
    with pytest.raises(ValueError, match=r'com\.example\.spaceRecord does not declare a space type'):
        SpaceType.from_lexicon(_parse_lexicon('com.example.spaceRecord.json'))


def test_space_type_has_no_collections_by_default() -> None:
    assert SpaceType(_GROUP, 'any').collections == ()


@pytest.mark.parametrize('key', ['any', 'nsid', 'tid', 'literal:self', 'literal:a:b'])
def test_space_type_accepts_a_key_type(key: str) -> None:
    assert SpaceType(_GROUP, key).key == key


@pytest.mark.parametrize(
    'key', ['', 'bogus', 'self', 'literal', 'literal:', 'literal:a/b', 'literal:.', 'literal:..', 'literal:self\n']
)
def test_space_type_refuses_a_key_that_is_not_a_key_type(key: str) -> None:
    with pytest.raises(ValueError, match="Space key must be 'any', 'nsid', 'tid' or 'literal:<record key>'"):
        SpaceType(_GROUP, key)


# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex-schema/src/schema/space.test.ts
def test_ref_for_defaults_the_key_of_a_literal_key() -> None:
    ref = SpaceType(_GROUP, 'literal:self').ref_for(_DID)

    assert str(ref) == 'at://did:example:123/space/com.example.group/self'


def test_ref_for_accepts_the_literal_key() -> None:
    assert SpaceType(_GROUP, 'literal:self').ref_for(_DID, 'self') == SpaceRef(_DID, _GROUP, 'self')


def test_ref_for_builds_a_ref_with_the_given_key() -> None:
    ref = SpaceType(_GROUP, 'tid').ref_for(_DID, '3jzfcijpj2z2a')

    assert ref == SpaceRef(_DID, _GROUP, '3jzfcijpj2z2a')


@pytest.mark.parametrize('skey', ['other', 'sel', 'selfself', ''])
def test_ref_for_refuses_a_key_that_is_not_the_literal_key(skey: str) -> None:
    with pytest.raises(ValueError, match='must be self'):
        SpaceType(_GROUP, 'literal:self').ref_for(_DID, skey)


@pytest.mark.parametrize('skey', [None, ''])
@pytest.mark.parametrize('key', ['any', 'tid', 'nsid'])
def test_ref_for_requires_a_key_without_a_literal_key(key: str, skey: t.Optional[str]) -> None:
    with pytest.raises(ValueError, match='is required'):
        SpaceType(_GROUP, key).ref_for(_DID, skey)


@pytest.mark.parametrize('skey', ['a/b', 'a b', '.', '..', 'key\n', 'k' * 513])
def test_ref_for_refuses_a_key_that_is_not_a_record_key(skey: str) -> None:
    with pytest.raises(InvalidAtUriError, match='Space URI'):
        SpaceType(_GROUP, 'any').ref_for(_DID, skey)


def test_ref_for_refuses_an_invalid_did() -> None:
    with pytest.raises(InvalidAtUriError, match='invalid space_did'):
        SpaceType(_GROUP, 'any').ref_for('alice.test', 'general')
