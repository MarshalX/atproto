from dataclasses import dataclass
from typing import Optional


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
class OptionsModelBase(ModelBase):
    headers: Optional[dict] = None
    # TODO(MarshalX)
    #  timeout: Optional[float]


@dataclass
class ResponseModelBase(ModelBase):
    pass
    # TODO
    # success: bool
    # headers: dict
