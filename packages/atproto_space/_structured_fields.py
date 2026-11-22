import base64
import re
import typing as t
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

_SP: t.Final = ' '
_OWS: t.Final = ' \t'

_MAX_INTEGER_DIGITS: t.Final = 15
_MAX_DECIMAL_INTEGER_DIGITS: t.Final = 12
_MAX_DECIMAL_FRACTION_DIGITS: t.Final = 3
_DECIMAL_QUANTUM: t.Final = Decimal(1).scaleb(-_MAX_DECIMAL_FRACTION_DIGITS)

_KEY: t.Final = re.compile(r'[a-z*][a-z0-9_.*-]*')
_NUMBER: t.Final = re.compile(r'(-?[0-9]+)(?:\.([0-9]*))?')
_STRING: t.Final = re.compile(r'"((?:[\x20\x21\x23-\x5b\x5d-\x7e]|\\["\\])*)"')
_TOKEN: t.Final = re.compile(r"[A-Za-z*][A-Za-z0-9!#$%&'*+.^_`|~:/-]*")
_BYTE_SEQUENCE: t.Final = re.compile(r':([A-Za-z0-9+/]*)=*:')
_BOOLEAN: t.Final = re.compile(r'\?([01])')

_STRING_CHARS: t.Final = re.compile(r'[ -~]*')
_STRING_ESCAPED_CHAR: t.Final = re.compile(r'\\(["\\])')
_STRING_CHAR_TO_ESCAPE: t.Final = re.compile(r'(["\\])')


@dataclass(frozen=True)
class Token:
    """Token: an unquoted word, which is not equal to the string of the same characters."""

    value: str


BareItem = t.Union[int, Decimal, str, Token, bytes, bool]


@dataclass(frozen=True)
class Item:
    """Bare item with its parameters."""

    value: BareItem
    params: t.Dict[str, BareItem] = field(default_factory=dict)


@dataclass(frozen=True)
class InnerList:
    """List of items with the parameters of the list."""

    items: t.List[Item]
    params: t.Dict[str, BareItem] = field(default_factory=dict)


Member = t.Union[Item, InnerList]


def _skip(text: str, position: int, chars: str) -> int:
    while position < len(text) and text[position] in chars:
        position += 1

    return position


def _parse_key(text: str, position: int) -> t.Tuple[str, int]:
    match = _KEY.match(text, position)
    if not match:
        raise ValueError(f'Invalid structured field. Expected a key at position {position}.')

    return match.group(), match.end()


def _parse_number(integer: str, fraction: t.Optional[str]) -> t.Union[int, Decimal]:
    digits = len(integer.lstrip('-'))
    if fraction is None:
        if digits > _MAX_INTEGER_DIGITS:
            raise ValueError(f'Invalid structured field. Integer {integer} is too long.')

        return int(integer)

    if digits > _MAX_DECIMAL_INTEGER_DIGITS or not 0 < len(fraction) <= _MAX_DECIMAL_FRACTION_DIGITS:
        raise ValueError(f'Invalid structured field. Decimal {integer}.{fraction} is out of range.')

    return Decimal(f'{integer}.{fraction}')


def _parse_byte_sequence(content: str) -> bytes:
    if len(content) % 4 == 1:
        raise ValueError('Invalid structured field. Byte sequence is not base64.')

    return base64.b64decode(content + '=' * (-len(content) % 4))


def _parse_bare_item(text: str, position: int) -> t.Tuple[BareItem, int]:
    match = _NUMBER.match(text, position)
    if match:
        return _parse_number(match.group(1), match.group(2)), match.end()

    match = _STRING.match(text, position)
    if match:
        return _STRING_ESCAPED_CHAR.sub(r'\1', match.group(1)), match.end()

    match = _TOKEN.match(text, position)
    if match:
        return Token(match.group()), match.end()

    match = _BYTE_SEQUENCE.match(text, position)
    if match:
        return _parse_byte_sequence(match.group(1)), match.end()

    match = _BOOLEAN.match(text, position)
    if match:
        return match.group(1) == '1', match.end()

    raise ValueError(f'Invalid structured field. Expected an item at position {position}.')


def _parse_params(text: str, position: int) -> t.Tuple[t.Dict[str, BareItem], int]:
    params: t.Dict[str, BareItem] = {}
    while text.startswith(';', position):
        key, position = _parse_key(text, _skip(text, position + 1, _SP))
        value: BareItem = True
        if text.startswith('=', position):
            value, position = _parse_bare_item(text, position + 1)

        params[key] = value

    return params, position


def _parse_item(text: str, position: int) -> t.Tuple[Item, int]:
    value, position = _parse_bare_item(text, position)
    params, position = _parse_params(text, position)

    return Item(value, params), position


def _parse_inner_list(text: str, position: int) -> t.Tuple[InnerList, int]:
    items: t.List[Item] = []
    position = _skip(text, position + 1, _SP)
    while not text.startswith(')', position):
        item, position = _parse_item(text, position)
        items.append(item)

        if not text.startswith((_SP, ')'), position):
            raise ValueError(f'Invalid structured field. Expected the end of an inner list at position {position}.')

        position = _skip(text, position, _SP)

    params, position = _parse_params(text, position + 1)

    return InnerList(items, params), position


def _parse_member(text: str, position: int) -> t.Tuple[Member, int]:
    if text.startswith('=(', position):
        return _parse_inner_list(text, position + 1)

    if text.startswith('=', position):
        return _parse_item(text, position + 1)

    params, position = _parse_params(text, position)

    return Item(True, params), position


def parse_item(value: str) -> Item:
    """Parse the field value of an item.

    Raises:
        :class:`ValueError`: The value is not an item.
    """
    item, position = _parse_item(value, _skip(value, 0, _SP))
    position = _skip(value, position, _SP)
    if position != len(value):
        raise ValueError(f'Invalid structured field. Unexpected character at position {position}.')

    return item


def parse_dictionary(value: str) -> t.Dict[str, Member]:
    """Parse the field value of a dictionary. A repeated key keeps its first place and its last value.

    Raises:
        :class:`ValueError`: The value is not a dictionary.
    """
    members: t.Dict[str, Member] = {}
    position = _skip(value, 0, _SP)
    while position < len(value):
        key, position = _parse_key(value, position)
        members[key], position = _parse_member(value, position)

        position = _skip(value, position, _OWS)
        if position == len(value):
            break

        if value[position] != ',':
            raise ValueError(f'Invalid structured field. Expected a comma at position {position}.')

        position = _skip(value, position + 1, _OWS)
        if position == len(value):
            raise ValueError('Invalid structured field. Unexpected comma at the end.')

    return members


def _serialize_key(key: str) -> str:
    if not _KEY.fullmatch(key):
        raise ValueError(f'Structured field can not have key {key!r}.')

    return key


def _serialize_integer(value: int) -> str:
    if abs(value) >= 10**_MAX_INTEGER_DIGITS:
        raise ValueError(f'Structured field can not hold integer {value}.')

    return str(value)


def _serialize_decimal(value: Decimal) -> str:
    try:
        rounded = value.quantize(_DECIMAL_QUANTUM, rounding=ROUND_HALF_EVEN)
    except InvalidOperation as e:
        raise ValueError(f'Structured field can not hold decimal {value}.') from e

    if not rounded.is_finite() or abs(rounded) >= 10**_MAX_DECIMAL_INTEGER_DIGITS:
        raise ValueError(f'Structured field can not hold decimal {value}.')

    sign = '-' if rounded < 0 else ''
    integer, _, fraction = f'{abs(rounded):f}'.partition('.')
    fraction = fraction.rstrip('0') or '0'

    return f'{sign}{integer}.{fraction}'


def _serialize_string(value: str) -> str:
    if not _STRING_CHARS.fullmatch(value):
        raise ValueError(f'Structured field can not hold string {value!r}.')

    escaped = _STRING_CHAR_TO_ESCAPE.sub(r'\\\1', value)

    return f'"{escaped}"'


def _serialize_token(token: Token) -> str:
    if not _TOKEN.fullmatch(token.value):
        raise ValueError(f'Structured field can not hold token {token.value!r}.')

    return token.value


def _serialize_bare_item(value: BareItem) -> str:
    if isinstance(value, bool):
        return '?1' if value else '?0'

    if isinstance(value, int):
        return _serialize_integer(value)

    if isinstance(value, Decimal):
        return _serialize_decimal(value)

    if isinstance(value, Token):
        return _serialize_token(value)

    if isinstance(value, bytes):
        return f':{base64.b64encode(value).decode("ascii")}:'

    return _serialize_string(value)


def _serialize_params(params: t.Mapping[str, BareItem]) -> str:
    serialized = ''
    for key, value in params.items():
        serialized += f';{_serialize_key(key)}'
        if value is not True:
            serialized += f'={_serialize_bare_item(value)}'

    return serialized


def serialize_item(item: Item) -> str:
    """Serialize an item, for example ``"atproto-space-commit";sf``.

    Raises:
        :class:`ValueError`: A value or a key has no serialization.
    """
    return _serialize_bare_item(item.value) + _serialize_params(item.params)


def serialize_inner_list(inner_list: InnerList) -> str:
    """Serialize an inner list, for example ``("a" "b";sf);keyid="x";tag="y"``.

    Raises:
        :class:`ValueError`: A value or a key has no serialization.
    """
    items = ' '.join(serialize_item(item) for item in inner_list.items)

    return f'({items}){_serialize_params(inner_list.params)}'


def serialize_dictionary(members: t.Mapping[str, Member]) -> str:
    """Serialize a dictionary, for example ``ver=1, repo="did:plc:x", sf``.

    Raises:
        :class:`ValueError`: A value or a key has no serialization.
    """
    serialized: t.List[str] = []
    for key, member in members.items():
        if isinstance(member, InnerList):
            serialized.append(f'{_serialize_key(key)}={serialize_inner_list(member)}')
        elif member.value is True:
            serialized.append(_serialize_key(key) + _serialize_params(member.params))
        else:
            serialized.append(f'{_serialize_key(key)}={serialize_item(member)}')

    return ', '.join(serialized)
