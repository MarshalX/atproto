from pydantic import BaseModel, ConfigDict

from atproto.exceptions import ModelFieldNotFoundError


class AtProtocolBase:
    ...


class ModelBase(BaseModel, AtProtocolBase):
    """Base class for all data classes.

    Provides square brackets [] notation to get attributes like in a dictionary.
    """

    model_config = ConfigDict(extra='forbid', populate_by_name=True, strict=True)

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


class UnknownDict(AtProtocolBase):
    pass


class UnknownRecord(ModelBase):
    pass


class RecordModelBase(UnknownRecord):
    pass
