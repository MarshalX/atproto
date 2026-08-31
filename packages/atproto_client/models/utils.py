import types
import typing as t

import typing_extensions as te
from pydantic import BaseModel, ValidationError
from pydantic_core import from_json, to_json

from atproto_client import models
from atproto_client.exceptions import (
    ModelError,
    ModelFieldNotFoundError,
)
from atproto_client.models.base import ModelBase, RecordModelBase
from atproto_client.models.blob_ref import BlobRef
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.record_registry import resolve_record_type
from atproto_client.models.unknown_type import UnknownRecordType

if t.TYPE_CHECKING:
    from atproto_client.request import Response

M = t.TypeVar('M')
R = t.TypeVar('R', bound=RecordModelBase)
ModelData: te.TypeAlias = t.Union[
    M, t.Dict[str, t.Any], None
]  # we assume that dict is JSON object. not list or primitive

_TYPE_SERVICE_FIELD = '$type'


def get_or_create(
    model_data: ModelData[M],
    model: t.Optional[t.Type[M]] = None,
    *,
    strict: bool = True,
    strict_string_format: bool = False,
) -> t.Optional[t.Union[M, UnknownRecordType, DotDict]]:
    """Get model instance from raw data.

    Note:
        The record could have additional fields and be completely custom.
        For example, third-party bsky clients add a "via"
        field to indicate that it was posted using a not official client.
        Such records are corresponding to the lexicon, but have additional fields.
        This is called "extended record".
        Extended records will be decoded to proper models with extra, non-typehinted fields available only in runtime.
        Unknown record types will be decoded to :obj:`atproto.xrpc_client.models.base.DotDict`.
        A union member with an unrecognized "$type" is decoded to a DotDict too, without failing
        the rest of the model.

    Note:
        By default, the method raises an exception on custom models if you have passed the expected model.
        To fall back to a :obj:`atproto.xrpc_client.models.base.DotDict` type, disable strict mode using the argument.

    Note:
        Model auto-resolve works only with a Record type for now.

    Args:
        model_data: Raw data.
        model: Class of the model or any another type. If None, it will be resolved automatically.
        strict: Disable fallback to dictionary (:obj:`atproto.xrpc_client.models.base.DotDict`)
            if it can't be properly deserialized in provided `model`. Will raise the exception instead.
        strict_string_format: Enable strict string format validation.

    Returns:
        Instance of ``model`` or :obj:`None` or
        :obj:`atproto.xrpc_client.models.dot_dict.DotDict` if `strict` is disabled.
    """
    try:
        model_instance = _get_or_create(model_data, model, strict=strict, strict_string_format=strict_string_format)
        if strict and model_instance is not None and (not model or not isinstance(model_instance, model)):
            raise ModelError(f"Can't properly parse model of type {model}")

        return model_instance
    except Exception:
        if strict or not isinstance(model_data, dict):
            raise

        return DotDict(model_data)


def _get_or_create(
    model_data: ModelData[M], model: t.Optional[t.Type[M]], *, strict: bool, strict_string_format: bool
) -> t.Optional[t.Union[M, UnknownRecordType, DotDict]]:
    if model_data is None:
        return None

    if model is None:
        if not isinstance(model_data, dict):
            return None

        # we are sure that this is dict because of check above
        model_data = t.cast('t.Dict[str, t.Any]', model_data)

        # resolve a record model by type and try to deserialize
        record_type: t.Any = model_data.get(_TYPE_SERVICE_FIELD)
        record_model = resolve_record_type(record_type) if isinstance(record_type, str) else None
        if record_model is None:
            return None

        return get_or_create(
            model_data,
            record_model,
            strict=strict,
            strict_string_format=strict_string_format,
        )

    if isinstance(model_data, model):
        return model_data

    try:
        if issubclass(model, BaseModel):
            return model.model_validate(model_data, context={'strict_string_format': strict_string_format})
        if not isinstance(model_data, t.Mapping):
            raise ModelError(f'Cannot parse model of type {model}')
        return model(**model_data)
    except ValidationError as e:
        raise ModelError(str(e)) from e


def get_response_model(response: 'Response', model: t.Type[M]) -> M:
    if model is bool:
        # Could not be False? Because the exception with errors will be raised from the server
        return t.cast('M', response.success)
    if model is bytes:
        return t.cast('M', response.content)

    if not isinstance(response.content, dict):
        raise ModelError("Can't properly parse response model because JSON is expected in response")

    # casting to M because of enabled strict mode
    return t.cast('M', get_or_create(response.content, model, strict=True))


def get_model_as_dict(model: t.Union[DotDict, BlobRef, ModelBase]) -> t.Dict[str, t.Any]:
    if isinstance(model, DotDict):
        return model.to_dict()

    return model.model_dump(exclude_none=True, by_alias=True)


def get_model_as_json(model: t.Union[DotDict, BlobRef, ModelBase]) -> str:
    if isinstance(model, DotDict):
        return to_json(get_model_as_dict(model)).decode('UTF-8')

    return model.model_dump_json(exclude_none=True, by_alias=True)


def is_json(json_data: t.Union[str, bytes]) -> bool:
    return load_json(json_data, strict=False) is not None


def load_json(json_data: t.Union[str, bytes], strict: bool = True) -> t.Optional[t.Dict[str, t.Any]]:
    try:
        return from_json(json_data)
    except ValueError:
        if strict:
            raise

        return None


class _RecordModule(t.Protocol[R]):
    """Protocol of a generated lexicon module that defines a Record."""

    Record: t.Type[R]


@t.overload
def is_record_type(model: t.Union[ModelBase, DotDict], expected_type: _RecordModule[R]) -> te.TypeGuard[R]: ...


@t.overload
def is_record_type(model: t.Union[ModelBase, DotDict], expected_type: t.Type[R]) -> te.TypeGuard[R]: ...


@t.overload
def is_record_type(model: t.Union[ModelBase, DotDict], expected_type: t.Union[str, types.ModuleType]) -> bool: ...


def is_record_type(model: t.Union[ModelBase, DotDict], expected_type: t.Any) -> bool:
    """Verify that the model is the expected Record type.

    Note:
        Passing a Python module or a Record class narrows the type of `model` for static type checkers.
        Narrowing is not performed for the NSID form because a string carries no type information.

    Warning:
        A custom or extended record that failed validation is decoded to
        :obj:`atproto_client.models.dot_dict.DotDict`.
        Such a model matches its own type by NSID, so the narrowed type is not guaranteed
        to be an instance of the Record class in runtime.

    Args:
        model: Model to be verified.
        expected_type: Excepted type.
            Could be NSID, Python Module, or Record class.

    Example:
        >>> from atproto import Client, models
        >>> from atproto_client.models import ids, is_record_type
        >>> client = Client()
        >>> client.login('username', 'pass')
        >>> record = client.com.atproto.repo.get_record(...)
        >>> # using NSID:
        >>> is_record_type(record.value, ids.AppBskyFeedPost)
        >>> # using Python module:
        >>> is_record_type(record.value, models.AppBskyFeedPost)
        >>> # using Record class:
        >>> is_record_type(record.value, models.AppBskyFeedPost.Record)

    Returns:
        :obj:`bool`: Is record or not.
    """
    if isinstance(expected_type, types.ModuleType):
        # for now, all records are defined in the Record class
        expected_type = getattr(expected_type, 'Record', None)

    if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
        py_type_field = expected_type.model_fields.get('py_type')
        expected_type = py_type_field.default if py_type_field else None

    if not isinstance(expected_type, str):
        return False

    if isinstance(model, DotDict):  # custom record
        try:
            return expected_type == model[_TYPE_SERVICE_FIELD]
        except ModelFieldNotFoundError:
            return False

    return expected_type == model.py_type


def create_strong_ref(model: ModelBase) -> models.ComAtprotoRepoStrongRef.Main:
    """Create a strong ref from the model.

    Args:
        model: Any model with `cid` and `uri` fields.

    Example:
        >>> from atproto import Client
        >>> client = Client()
        >>> client.login('my-handle', 'my-password')
        >>> response = client.send_post(text='Hello World from Python!')
        >>> strong_ref = create_strong_ref(response)

    Returns:
        :obj:`atproto.xrpc_client.models.com.atproto.repo.strong_ref.Main`: Strong ref.
    """
    if hasattr(model, 'cid') and hasattr(model, 'uri'):
        return models.ComAtprotoRepoStrongRef.Main(cid=model.cid, uri=model.uri)

    raise ModelError('Could not create strong ref from model')
