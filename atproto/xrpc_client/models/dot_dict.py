import typing as t
from copy import deepcopy

import typing_extensions as te
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from atproto.xrpc_client.models.base import UnknownDict


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

    def __init__(self, data: dict) -> None:
        self._data = data
        for k, v in self._data.items():
            self.__setitem__(k, v)

    def to_dict(self) -> dict:
        """Unwrap DotDict to Python built-in dict."""
        return deepcopy(self._data)

    def __getitem__(self, item: str) -> t.Optional[t.Any]:
        return self._data.get(item)

    __getattr__ = __getitem__

    def __setitem__(self, key: str, value: t.Any) -> None:
        if key == '_data':
            super().__setattr__(key, value)
            return

        self._data.__setitem__(key, DotDict.__convert(value))

    __setattr__ = __setitem__

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, DotDict):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other

        raise NotImplementedError

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __reduce_ex__(self, protocol: int):
        return getattr(self._data, '__reduce_ex__', None)(protocol)

    def __reduce__(self):
        return getattr(self._data, '__reduce__', None)()

    @staticmethod
    def __convert(obj: t.Any) -> t.Any:
        if isinstance(obj, dict):
            return DotDict(obj)
        if isinstance(obj, list):
            return [DotDict.__convert(v) for v in obj]
        if isinstance(obj, set):
            return {DotDict.__convert(v) for v in obj}
        if isinstance(obj, tuple):
            return tuple(DotDict.__convert(v) for v in obj)
        return obj


class _DotDictPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: t.Callable[[t.Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * dicts will be parsed as `DotDict` instances with the int as the _data attribute
        * `DotDict` instances will be parsed as `DotDict` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a dict
        """

        def validate_from_dict(value: dict) -> DotDict:
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
