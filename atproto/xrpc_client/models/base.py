from dataclasses import dataclass


@dataclass
class ModelBase:
    pass


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
