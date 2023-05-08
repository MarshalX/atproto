from dataclasses import dataclass

from atproto.exceptions import ModelFieldNotFoundError


@dataclass
class ModelBase:
    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

        raise ModelFieldNotFoundError(f"Can't find field '{item}' in the object of type {type(self)}.")


@dataclass
class ParamsModelBase(ModelBase):
    pass


@dataclass
class DataModelBase(ModelBase):
    pass


@dataclass
class ResponseModelBase(ModelBase):
    pass


@dataclass
class RecordModelBase(ModelBase):
    pass
