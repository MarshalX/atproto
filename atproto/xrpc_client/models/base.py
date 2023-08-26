import typing as t
from copy import deepcopy

import typing_extensions as te
from pydantic import BaseModel, ConfigDict, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from atproto.exceptions import ModelFieldNotFoundError


class ModelBase(BaseModel):
    """Base class for all data classes.

    Provides square brackets [] notation to get attributes like in a dictionary.
    """

    model_config = ConfigDict(extra='forbid')

    def __getitem__(self, item: str):
        if hasattr(self, item):
            return getattr(self, item)

        raise ModelFieldNotFoundError(f"Can't find field '{item}' in the object of type {type(self)}.")


class ParamsModelBase(ModelBase):
    pass


class DataModelBase(ModelBase):
    pass


class ResponseModelBase(ModelBase):
    pass


class UnknownDict:
    pass


class DotDict(UnknownDict):
    """Dot notation for dictionaries.

    Note:
        If the record is out of the official lexicon, it`s impossible to deserialize it to a proper data model.
        Such models will fall back to dictionaries.
        All unknown "Union" types will also be caught as dicts.
        This class exists to provide an ability to use such fallbacks as “real” data models.
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def to_dict(self) -> dict:
        return deepcopy(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __getattr__(self, item: str) -> t.Optional[t.Any]:
        return self._data.get(item)

    def __setattr__(self, key: str, value: t.Any) -> None:
        if key == '_data':
            super().__setattr__(key, value)
            return

        self._data[key] = value

    def __delattr__(self, item) -> None:
        del self._data[item]

    def __eq__(self, other: t.Any) -> bool:
        return self._data == other

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)


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


class UnknownRecord(ModelBase):
    pass


class RecordModelBase(UnknownRecord):
    pass
