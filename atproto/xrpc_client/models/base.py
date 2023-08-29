from pydantic import BaseModel, ConfigDict

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


class UnknownRecord(ModelBase):
    pass


class RecordModelBase(UnknownRecord):
    pass
