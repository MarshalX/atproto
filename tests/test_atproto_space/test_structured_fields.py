import base64
import json
import os
import typing as t
from decimal import Decimal

import pytest
from atproto_space._structured_fields import (
    InnerList,
    Item,
    Member,
    Token,
    parse_dictionary,
    parse_item,
    serialize_dictionary,
    serialize_inner_list,
    serialize_item,
)

# Ref: https://github.com/httpwg/structured-field-tests/tree/4a4782f8234512af133f6f57c4ca998578b57110
_TESTS_DIR_PATH = os.path.join(os.path.dirname(__file__), 'structured-field-tests')

_SUPPORTED_FILES = (
    'binary.json',
    'boolean.json',
    'dictionary.json',
    'examples.json',
    'item.json',
    'number.json',
    'param-dict.json',
    'string.json',
    'token.json',
    os.path.join('serialisation-tests', 'number.json'),
)
_UNSUPPORTED_FILES = ('date.json', 'display-string.json')
_HEADER_TYPES = ('item', 'dictionary')

# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/mac.test.ts
_COMMIT_HEADER = (
    'ver=1, repo="did:example:alice", space="at://did:example:space/space/app.bsky.group/test", '
    'rev="3kbcq3p7ad400", data=:AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE=:'
)
_RECORD_HEADER = (
    'uri="at://did:example:space/space/app.bsky.group/test/did:example:alice/app.bsky.feed.post/1", '
    'cid="bafyreidefdycgbfy3oglcb6ism3eqhyp5llsrpzxjsuac2gsy4mtrtx244"'
)
_COMMIT_COMPONENTS = '("atproto-space-commit";sf)'
_COMMIT_PARAMS = f'{_COMMIT_COMPONENTS};keyid="did:key:zDnaExample";tag="atproto-space-commit"'
# Ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/space/src/http-signature.test.ts
_CREDENTIAL_PARAMS = (
    '("authorization" "atproto-space-audience");alg="ecdsa-p256-sha256";created=1618884473;'
    'keyid="did:key:zDnaExample";tag="atproto-space-credential"'
)


def _decode_typed_value(value: t.Dict[str, t.Any]) -> t.Any:
    if value.get('__type') == 'token':
        return Token(value['value'])

    if value.get('__type') == 'binary':
        return base64.b32decode(value['value'])

    return value


def _load_test_cases(filenames: t.Tuple[str, ...]) -> t.List[t.Dict[str, t.Any]]:
    test_cases: t.List[t.Dict[str, t.Any]] = []
    for filename in filenames:
        with open(os.path.join(_TESTS_DIR_PATH, filename), encoding='UTF-8') as file:
            test_cases.extend(json.load(file, parse_float=Decimal, object_hook=_decode_typed_value))

    return [test_case for test_case in test_cases if test_case['header_type'] in _HEADER_TYPES]


_TEST_CASES = _load_test_cases(_SUPPORTED_FILES)


def _get_field_value(lines: t.List[str]) -> str:
    return ', '.join(lines)


def _to_item(value: t.List[t.Any]) -> Item:
    return Item(value[0], dict(value[1]))


def _to_member(value: t.List[t.Any]) -> Member:
    items, params = value
    if isinstance(items, list):
        return InnerList([_to_item(item) for item in t.cast('t.List[t.Any]', items)], dict(params))

    return _to_item(value)


def _to_expected(test_case: t.Dict[str, t.Any]) -> t.Union[Item, t.Dict[str, Member]]:
    if test_case['header_type'] == 'item':
        return _to_item(test_case['expected'])

    return {key: _to_member(value) for key, value in test_case['expected']}


def _with_types(value: t.Any) -> t.Any:
    """Tell apart values that are equal in Python, such as ``1``, ``True`` and ``Decimal(1)``."""
    if isinstance(value, Item):
        return 'item', _with_types(value.value), _with_types(value.params)

    if isinstance(value, InnerList):
        return 'inner list', [_with_types(item) for item in value.items], _with_types(value.params)

    if isinstance(value, dict):
        return [(key, _with_types(member)) for key, member in t.cast('t.Dict[str, t.Any]', value).items()]

    return type(value).__name__, value


def _parse(test_case: t.Dict[str, t.Any]) -> t.Union[Item, t.Dict[str, Member]]:
    field_value = _get_field_value(test_case['raw'])
    if test_case['header_type'] == 'item':
        return parse_item(field_value)

    return parse_dictionary(field_value)


def _serialize(test_case: t.Dict[str, t.Any]) -> str:
    expected = _to_expected(test_case)
    if isinstance(expected, Item):
        return serialize_item(expected)

    return serialize_dictionary(expected)


@pytest.mark.parametrize(
    'test_case',
    [test_case for test_case in _TEST_CASES if 'raw' in test_case and not test_case.get('must_fail')],
    ids=lambda x: x['name'],
)
def test_parse(test_case: t.Dict[str, t.Any]) -> None:
    assert _with_types(_parse(test_case)) == _with_types(_to_expected(test_case))


@pytest.mark.parametrize(
    'test_case',
    [test_case for test_case in _TEST_CASES if 'raw' in test_case and test_case.get('must_fail')],
    ids=lambda x: x['name'],
)
def test_parse_invalid(test_case: t.Dict[str, t.Any]) -> None:
    with pytest.raises(ValueError, match='Invalid structured field'):
        _parse(test_case)


@pytest.mark.parametrize(
    'test_case',
    _load_test_cases(_UNSUPPORTED_FILES),
    ids=lambda x: x['name'],
)
def test_parse_unsupported(test_case: t.Dict[str, t.Any]) -> None:
    with pytest.raises(ValueError, match='Invalid structured field'):
        _parse(test_case)


@pytest.mark.parametrize(
    'test_case',
    [test_case for test_case in _TEST_CASES if 'expected' in test_case and not test_case.get('must_fail')],
    ids=lambda x: x['name'],
)
def test_serialize(test_case: t.Dict[str, t.Any]) -> None:
    canonical = test_case['canonical'] if 'canonical' in test_case else test_case['raw']

    assert _serialize(test_case) == _get_field_value(canonical)


@pytest.mark.parametrize(
    'test_case',
    [test_case for test_case in _TEST_CASES if 'expected' in test_case and test_case.get('must_fail')],
    ids=lambda x: x['name'],
)
def test_serialize_invalid(test_case: t.Dict[str, t.Any]) -> None:
    with pytest.raises(ValueError, match='Structured field can not'):
        _serialize(test_case)


def test_every_vendored_case_is_used() -> None:
    assert len(_TEST_CASES) == 162
    assert len(_load_test_cases(_UNSUPPORTED_FILES)) == 44


@pytest.mark.parametrize(
    'value',
    [
        _COMMIT_HEADER,
        _RECORD_HEADER,
        f'mac={_COMMIT_PARAMS}',
        f'sig1={_COMMIT_PARAMS}',
        f'mac={_COMMIT_COMPONENTS};tag="atproto-space-commit";created=1700000000;keyid="did:key:zDnaExample"',
        f'mac={_COMMIT_PARAMS};alg="hmac-sha256"',
        f'other=("content-digest");tag="other", m={_COMMIT_PARAMS}',
        'mac=("atproto-space-commit";sf "authorization");tag="atproto-space-commit"',
        'mac=("atproto-space-commit";sf=?0);tag="atproto-space-commit"',
        'mac=:1h+Y4FYlVeulHfrXICCPNKTCClsE753w5a4KuEPYc9M=:',
        'sig=("authorization" "atproto-space-audience");tag="atproto-space-credential"',
        f'other=("authorization");keyid="other", custom={_CREDENTIAL_PARAMS}',
        'other=:YWJj:, custom=:c2lnbmF0dXJl:',
    ],
)
def test_canonical_header_round_trips(value: str) -> None:
    assert serialize_dictionary(parse_dictionary(value)) == value


@pytest.mark.parametrize(
    'value',
    [
        _COMMIT_HEADER.replace(', ', ',   '),
        _COMMIT_HEADER.replace(', ', ','),
        _COMMIT_HEADER.replace(', ', '\t,\t'),
        f'  {_COMMIT_HEADER}  ',
        _COMMIT_HEADER.replace('AQE=:', 'AQE:').replace('ver=1', 'ver=01'),
    ],
)
def test_commit_header_is_normalized(value: str) -> None:
    assert serialize_dictionary(parse_dictionary(value)) == _COMMIT_HEADER


def test_commit_header_members() -> None:
    members = parse_dictionary(_COMMIT_HEADER)

    assert _with_types(members) == _with_types(
        {
            'ver': Item(1),
            'repo': Item('did:example:alice'),
            'space': Item('at://did:example:space/space/app.bsky.group/test'),
            'rev': Item('3kbcq3p7ad400'),
            'data': Item(b'\x01' * 32),
        }
    )


def test_signature_input_members() -> None:
    members = parse_dictionary(f'other=("content-digest");tag="other", m={_COMMIT_PARAMS};created=1700000000')
    member = members['m']

    assert isinstance(member, InnerList)
    assert member.items == [Item('atproto-space-commit', {'sf': True})]
    assert member.params == {'keyid': 'did:key:zDnaExample', 'tag': 'atproto-space-commit', 'created': 1700000000}
    assert serialize_inner_list(member) == f'{_COMMIT_PARAMS};created=1700000000'
    assert serialize_inner_list(InnerList(member.items)) == _COMMIT_COMPONENTS
    assert [serialize_item(item) for item in member.items] == ['"atproto-space-commit";sf']


def test_token_is_not_a_string() -> None:
    members = parse_dictionary('tag=atproto-space-commit, alg="hmac-sha256"')

    assert members['tag'] == Item(Token('atproto-space-commit'))
    assert members['tag'] != Item('atproto-space-commit')
    assert members['alg'] == Item('hmac-sha256')
    assert serialize_dictionary(members) == 'tag=atproto-space-commit, alg="hmac-sha256"'


def test_parameters_keep_the_last_value_of_a_repeated_key() -> None:
    item = parse_item('1;a=1;b=2;a=3')

    assert list(item.params.items()) == [('a', 3), ('b', 2)]


@pytest.mark.parametrize(
    'value',
    [
        'ver=1, repo="did:example:alice',
        'mac=("atproto-space-commit";sf',
        'mac=("atproto-space-commit"sf)',
        'mac=("atproto-space-commit";sf)tag="x"',
        'mac=(("a"))',
        'sig=:c2ln',
        'sig=:c2ln:=',
        'sig=:c:',
        'sig=:c2lnc:',
        'ver=\u0661',
        'Ver=1',
        'ver=1;',
        'a=1 b=2',
    ],
)
def test_parse_dictionary_invalid(value: str) -> None:
    with pytest.raises(ValueError, match='Invalid structured field'):
        parse_dictionary(value)


@pytest.mark.parametrize(
    'item',
    [
        Item('füü'),
        Item('line\nbreak'),
        Item(Token('1a')),
        Item(Token('a b')),
        Item(Token('')),
        Item(10**15),
        Item(Decimal('NaN')),
        Item(Decimal('Infinity')),
        Item(Decimal('1e40')),
        Item(1, {'Key': 1}),
        Item(1, {'': 1}),
        Item(1, {'key': 'füü'}),
    ],
)
def test_serialize_item_invalid(item: Item) -> None:
    with pytest.raises(ValueError, match='Structured field can not'):
        serialize_item(item)


def test_serialize_dictionary_invalid() -> None:
    with pytest.raises(ValueError, match='Structured field can not'):
        serialize_dictionary({'1a': Item(1)})

    with pytest.raises(ValueError, match='Structured field can not'):
        serialize_dictionary({'a': InnerList([Item('füü')])})
