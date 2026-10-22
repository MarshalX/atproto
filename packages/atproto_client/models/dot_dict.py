import re
import typing as t
from collections import abc
from copy import deepcopy

import typing_extensions as te
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from atproto_client.models.base import UnknownDict


def _convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def _convert_snake_case_to_camel_case(string: str) -> str:
    s = ''.join([w.capitalize() for w in string.split('_')])
    return s[0].lower() + s[1:]


def _is_snake_case(string: str) -> bool:
    # same as `string == _convert_camel_case_to_snake_case(string)`, which only changes strings with uppercase
    return string == string.lower()


def _convert_to_opposite_case(string: str) -> str:
    if _is_snake_case(string):
        return _convert_snake_case_to_camel_case(string)
    return _convert_camel_case_to_snake_case(string)


class DotDict(UnknownDict):
    """Dot notation for dictionaries.

    Note:
        If the record is out of the official lexicon, it`s impossible to deserialize it to a proper data model.
        Such models will fall back to dictionaries.
        All unknown "Union" types will also be caught as dicts.
        This class exists to provide an ability to use such fallbacks as “real” data models.

    Example:
        >>> test_data = {'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}, 4, 5]}
        >>> model = DotDict(test_data)
        >>> assert isinstance(model, DotDict)
        >>> assert model.nonExistingField is None
        >>> assert model.a == 1
        >>> assert model['a'] == 1
        >>> assert model['b']['c'] == 2
        >>> assert model.b.c == 2
        >>> assert model.b['c'] == 2
        >>> assert model['b'].c == 2
        >>> assert model.d[0].e == 3
        >>> assert model['d'][0]['e'] == 3
        >>> assert model['d'][0].e == 3
        >>> assert model['d'][1] == 4
        >>> assert model['d'][2] == 5
        >>> model['d'][0]['e'] = 6
        >>> assert model['d'][0]['e'] == 6
        >>> assert DotDict(test_data) == DotDict(test_data)
        >>> assert model.to_dict() == test_data
    """

    __slots__ = ('__weakref__', '_data')

    _data: t.Dict[str, t.Any]

    def __init__(self, data: t.Dict[str, t.Any]) -> None:
        self._data = {key: _deep_copy(value, DotDict) for key, value in data.items()}

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Unwrap DotDict to Python built-in dict."""
        return _to_dict(self._data)

    def __getitem__(self, item: str) -> t.Any:
        value = self._data.get(item)
        if value is not None:
            return value

        return self._data.get(_convert_to_opposite_case(item))

    __getattr__ = __getitem__

    def __setitem__(self, key: str, value: t.Any) -> None:
        if key == '_data':
            object.__setattr__(self, key, value)
            return

        # we store the field in case that was firstly meet to not create duplicates
        if key not in self._data and _is_snake_case(key):
            key = _convert_snake_case_to_camel_case(key)

        self._data[key] = _deep_copy(value, DotDict)

    __setattr__ = __setitem__

    def __iter__(self) -> t.Iterator[str]:
        yield from iter(self._data)

    def keys(self) -> abc.KeysView[str]:
        return self._data.keys()

    def values(self) -> abc.ValuesView[t.Any]:
        return self._data.values()

    def items(self) -> abc.ItemsView[str, t.Any]:
        return self._data.items()

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: t.Any) -> bool:
        return item in self._data

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DotDict):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other

        raise NotImplementedError

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __reduce_ex__(self, protocol: te.SupportsIndex) -> t.Union[str, t.Tuple[t.Any, ...]]:
        return self._data.__reduce_ex__(protocol)

    def __reduce__(self) -> t.Union[str, t.Tuple[t.Any, ...]]:
        return self._data.__reduce__()


#: Leaves that a deep copy returns as is.
_ATOMIC_TYPES = frozenset({str, int, float, bool, bytes, type(None)})


def _deep_copy(obj: t.Any, copy_dict: t.Callable[[t.Dict[str, t.Any]], t.Any]) -> t.Any:
    """Deep copy ``obj``, building every dict, a :obj:`DotDict`'s included, with ``copy_dict``."""
    obj_type = type(obj)
    if obj_type in _ATOMIC_TYPES:
        return obj
    # exact types first: they are the common case and skip the isinstance() checks
    if obj_type is dict:
        return copy_dict(obj)
    if obj_type is list:
        return [_deep_copy(v, copy_dict) for v in obj]
    if isinstance(obj, DotDict):
        return copy_dict(obj._data)
    if isinstance(obj, dict):
        return copy_dict(t.cast('t.Dict[str, t.Any]', obj))
    if isinstance(obj, list):
        return [_deep_copy(v, copy_dict) for v in t.cast('t.List[t.Any]', obj)]
    if isinstance(obj, set):
        return {_deep_copy(v, copy_dict) for v in t.cast('t.Set[t.Any]', obj)}
    if isinstance(obj, tuple):
        return tuple(_deep_copy(v, copy_dict) for v in t.cast('t.Tuple[t.Any]', obj))
    return deepcopy(obj)


def _to_dict(data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {key: _deep_copy(value, _to_dict) for key, value in data.items()}


class _DotDictPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: t.Callable[[t.Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """We return a pydantic_core.CoreSchema that behaves in the following ways below.

        * dicts will be parsed as `DotDict` instances with the int as the _data attribute
        * `DotDict` instances will be parsed as `DotDict` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a dict
        """

        def validate_from_dict(value: t.Dict[str, t.Any]) -> DotDict:
            return DotDict(value)

        from_dict_schema = core_schema.chain_schema(
            [
                core_schema.dict_schema(),
                core_schema.no_info_plain_validator_function(validate_from_dict),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_dict_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(DotDict),
                    from_dict_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.to_dict()),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `dict`
        return handler(core_schema.dict_schema())


DotDictType = te.Annotated[DotDict, _DotDictPydanticAnnotation]
