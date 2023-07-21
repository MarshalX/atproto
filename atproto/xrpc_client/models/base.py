from atproto.exceptions import ModelFieldNotFoundError


class ModelBase:
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
    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, item):
        return self._data.get(item)

    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
            return

        self._data[key] = value

    def __delattr__(self, item):
        del self._data[item]


class UnknownRecord(UnknownDict):
    pass


class RecordModelBase(UnknownRecord):
    pass
