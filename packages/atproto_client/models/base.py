import os
import threading
import typing as t
import warnings

import typing_extensions as te
from pydantic import BaseModel, ConfigDict, Field, alias_generators, model_validator

from atproto_client.exceptions import ModelFieldNotFoundError

#: Most models come in a couple of shapes. The cap bounds memory if some producer varies them a lot.
_MAX_SHARED_FIELDS_SETS_PER_MODEL = 16


def _alias_generator(name: str) -> str:
    return alias_generators.to_camel(name).removesuffix('_')


class _SharedFieldsSet(t.Set[str]):
    """``__pydantic_fields_set__`` shared by all models with the same set fields. Never mutated in place.

    pydantic-core accepts only a :obj:`set` there, so it is a subclass that marks the set as shared.
    Copies and pickles are plain sets.
    """

    __slots__ = ()

    def __reduce__(self) -> t.Tuple[t.Any, ...]:
        return set, (list(self),)


#: Without the GIL, two threads unsharing one model at once would each install a copy and lose an update.
_UNSHARE_LOCK = threading.Lock()


def _unshare_fields_set(model: BaseModel) -> None:
    if type(model.__pydantic_fields_set__) is not _SharedFieldsSet:
        return

    with _UNSHARE_LOCK:
        fields_set = model.__pydantic_fields_set__
        if type(fields_set) is _SharedFieldsSet:
            object.__setattr__(model, '__pydantic_fields_set__', set(fields_set))


class AtProtocolBase:
    __slots__ = ()


class ModelBase(BaseModel, AtProtocolBase):
    """Base class for all data classes.

    Provides square brackets [] notation to get attributes like in a dictionary.

    Note:
        Models with the same set fields share one ``__pydantic_fields_set__`` until one of them is modified.
        A set per model is often the largest part of its memory.
    """

    model_config = ConfigDict(extra='allow', alias_generator=_alias_generator, populate_by_name=True, strict=True)

    __atproto_shared_fields_sets__: t.ClassVar[t.List[_SharedFieldsSet]] = []

    @classmethod
    @te.override
    def __pydantic_init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        cls.__atproto_shared_fields_sets__ = []

    def __getitem__(self, item: str) -> t.Any:
        if hasattr(self, item):
            return getattr(self, item)

        raise ModelFieldNotFoundError(f"Can't find field '{item}' in the object of type {type(self)}.")

    @model_validator(mode='after')
    def __after_validation(self) -> 'ModelBase':
        if self.__pydantic_extra__:
            if os.environ.get('ATPROTO_LEXICON_WARN', '0') == '1':
                # used for debugging purposes because gives false positives due to the way pydantic works
                warnings.warn(
                    f'Extra fields found in the object of type {type(self)}: {self.model_extra}. '  # noqa: S608
                    f'Probably you are using the old version of SDK. '
                    f'Please update it using `pip install -U atproto`. '
                    f'In case you are working with custom lexicon ignore this warning. '
                    f'It is also possible that you are working with extended record. '
                    f'To disable this warning set `ATPROTO_LEXICON_WARN` to `0` in the environment variables.',
                    stacklevel=0,
                )

            # extra keys are arbitrary, so models with them are not worth sharing a set
            return self

        fields_set = self.__pydantic_fields_set__
        shared_sets = type(self).__atproto_shared_fields_sets__
        for shared in shared_sets:
            # cheaper than building a hashable key
            if shared == fields_set:
                object.__setattr__(self, '__pydantic_fields_set__', shared)
                return self

        if len(shared_sets) < _MAX_SHARED_FIELDS_SETS_PER_MODEL:
            shared = _SharedFieldsSet(fields_set)
            shared_sets.append(shared)
            object.__setattr__(self, '__pydantic_fields_set__', shared)

        return self

    @te.override
    def __setattr__(self, name: str, value: t.Any) -> None:
        _unshare_fields_set(self)
        super().__setattr__(name, value)

    @te.override
    def __setstate__(self, state: t.Dict[t.Any, t.Any]) -> None:
        super().__setstate__(state)
        # models pickled together come back holding one plain set, so each needs its own
        object.__setattr__(self, '__pydantic_fields_set__', set(self.__pydantic_fields_set__))

    @property
    @te.override
    def model_fields_set(self) -> t.Set[str]:
        """The set of fields that have been explicitly set on this model instance."""
        _unshare_fields_set(self)
        return self.__pydantic_fields_set__

    @property
    @te.override
    def __fields_set__(self) -> t.Set[str]:
        _unshare_fields_set(self)
        return super().__fields_set__  # pyrefly: ignore[deprecated]


class ParamsModelBase(ModelBase):
    pass


class DataModelBase(ModelBase):
    pass


class ResponseModelBase(ModelBase):
    pass


class SugarResponseModelBase(ResponseModelBase):
    pass


class UnknownDict(AtProtocolBase):
    __slots__ = ()


class UnknownRecord(ModelBase):
    pass


class UnknownUnionModel(ModelBase):
    py_type: str = Field(alias='$type')


class RecordModelBase(UnknownRecord):
    pass
