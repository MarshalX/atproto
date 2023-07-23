import typing as t
from copy import deepcopy

from atproto.exceptions import ModelFieldNotFoundError


class ModelBase:
    """Base class for all data classes.

    Provides square brackets [] notation to get attributes like in a dictionary.
    """

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


class UnknownDict(ModelBase):
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


class UnknownRecord(UnknownDict):
    pass


class RecordModelBase(UnknownRecord):
    pass
