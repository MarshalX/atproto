import dataclasses
import json
import types
import typing as t
from enum import Enum

import typing_extensions as te
from dacite import Config, exceptions, from_dict

from atproto.cid import CID
from atproto.exceptions import (
    MissingValueError,
    ModelError,
    ModelFieldError,
    ModelFieldNotFoundError,
    UnexpectedFieldError,
    WrongTypeError,
)
from atproto.xrpc_client.models.base import DotDict, ModelBase, UnknownDict
from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models.type_conversion import RECORD_TYPE_TO_MODEL_CLASS
from atproto.xrpc_client.models.unknown_type import UnknownRecordType

if t.TYPE_CHECKING:
    from atproto.xrpc_client.request import Response

M = t.TypeVar('M')
ModelData: te.TypeAlias = t.Union[M, dict, None]

_TYPE_SERVICE_FIELD = '$type'


def _unknown_type_hook(data: dict) -> t.Union[UnknownRecordType, DotDict]:
    if _TYPE_SERVICE_FIELD in data:
        return get_or_create(data, strict=False)
    # any another unknown (not described by lexicon) type
    return DotDict(data)


def _decode_cid_hook(ref: t.Union[CID, str]) -> CID:
    if isinstance(ref, CID):
        return ref

    return CID.decode(ref)


_TYPE_HOOKS = {
    BlobRef: lambda ref: BlobRef.from_dict(ref),
    CID: _decode_cid_hook,
    UnknownDict: _unknown_type_hook,
}
_DACITE_CONFIG = Config(cast=[Enum], type_hooks=_TYPE_HOOKS)


def get_or_create(
    model_data: ModelData, model: t.Optional[t.Type[M]] = None, *, strict: bool = True
) -> t.Optional[t.Union[M, UnknownRecordType, DotDict]]:
    """Get model instance from raw data.

    Note:
        The record could have custom fields and be completely custom.
        For example, custom bsky clients add a "via" field to indicate that it was posted using a not official client.
        Such custom types can't be decoded into proper models,
        and will be decoded to :obj:`atproto.xrpc_client.models.base.DotDict`.

    Note:
        By default, the method raises an exception on custom models.
        To fall back to a :obj:`atproto.xrpc_client.models.base.DotDict` type, disable strict mode using the argument.

    Note:
        Model auto-resolve works only with a Record type for now.

    Args:
        model_data: Raw data.
        model: Class of the model or any another type. If None, it will be resolved automatically.
        strict: Disable fallback to dictionary (:obj:`atproto.xrpc_client.models.base.DotDict`)
            if can't be properly deserialized. Will raise the exception instead.

    Returns:
        Instance of :obj:`model` or :obj:`None` or
        :obj:`atproto.xrpc_client.models.base.DotDict` if `strict` is disabled.
    """
    try:
        model_instance = _get_or_create(model_data, model, strict=strict)
        if strict and model_instance is not None and not isinstance(model_instance, model):
            raise ModelError(f"Can't properly parse model of type {model}")

        return model_instance
    except Exception as e:  # noqa: BLE001
        if strict:
            raise e

        return DotDict(model_data)


def _validate_unexpected_fields(model_data: ModelData, model: t.Type[M]) -> None:
    model_type = None
    if isinstance(model_data, dict):
        # preserve the value of the service field to restore it later in case of fallback
        model_type = model_data.pop(_TYPE_SERVICE_FIELD, None)

    try:
        model(**model_data)
        return
    except Exception as e:
        if model_type:
            # restore service field to include it in the fall backed model (DotDict)
            model_data[_TYPE_SERVICE_FIELD] = model_type

        raise e


def _get_or_create(
    model_data: ModelData, model: t.Type[M], *, strict: bool
) -> t.Optional[t.Union[M, UnknownRecordType, DotDict]]:
    if model_data is None:
        return None

    if model is None:
        # resolve a record model by type and try to deserialize
        record_type = model_data.get(_TYPE_SERVICE_FIELD)
        if record_type not in RECORD_TYPE_TO_MODEL_CLASS:
            return None

        return get_or_create(model_data, RECORD_TYPE_TO_MODEL_CLASS[record_type], strict=strict)

    if isinstance(model_data, model):
        return model_data

    try:
        _validate_unexpected_fields(model_data, model)
        return from_dict(model, model_data, config=_DACITE_CONFIG)
    except TypeError as e:
        # FIXME(MarshalX): "Params missing 1 required positional argument: 'rkey'" should raise another error
        msg = str(e).replace('__init__()', model.__name__)
        raise UnexpectedFieldError(msg) from e
    except exceptions.MissingValueError as e:
        raise MissingValueError(str(e)) from e
    except exceptions.WrongTypeError as e:
        raise WrongTypeError(str(e)) from e
    except exceptions.DaciteFieldError as e:
        raise ModelFieldError(str(e)) from e
    except exceptions.DaciteError as e:
        raise ModelError(str(e)) from e


def get_response_model(response: 'Response', model: t.Type[M]) -> M:
    if model is bool:
        # Could not be False? Because the exception with errors will be raised from the server
        return response.success

    # return is optional if response.content is None, but doesn't occur in practice
    return get_or_create(response.content, model)


def _handle_dict_key(key: str) -> str:
    if key == '_type':  # System field. Replaced to original $ symbol because it is not allowed in Python.
        return _TYPE_SERVICE_FIELD

    return key


def _handle_dict_value(ref: t.Any) -> t.Any:
    if isinstance(ref, BlobRef):
        return ref.to_dict()
    if isinstance(ref, CID):
        return ref.encode()

    return ref


def _model_as_dict_factory(value) -> dict:
    # exclude None values and process keys and values
    return {_handle_dict_key(k): _handle_dict_value(v) for k, v in value if v is not None}


def get_model_as_dict(model: t.Union[BlobRef, ModelBase]) -> dict:
    if isinstance(model, (BlobRef, DotDict)):
        return model.to_dict()

    if not dataclasses.is_dataclass(model):
        raise ModelError('Invalid model')

    return dataclasses.asdict(model, dict_factory=_model_as_dict_factory)


def get_model_as_json(model: t.Union[BlobRef, ModelBase]) -> str:
    return json.dumps(get_model_as_dict(model))


def is_json(json_data: t.Union[str, bytes]) -> bool:
    if isinstance(json_data, bytes):
        json_data.decode('UTF-8')

    try:
        json.loads(json_data)
        return True
    except:  # noqa
        return False


def is_record_type(model: ModelBase, expected_type: t.Union[str, types.ModuleType]) -> bool:
    """Verify that the model is the expected Record type.

    Args:
        model: Model to be verified.
        expected_type: Excepted type.
            Could be NSID or Python Module.

    Example:
        >>> from atproto import Client, models
        >>> from atproto.xrpc_client.models import ids, is_record_type
        >>> client = Client()
        >>> client.login('username', 'pass')
        >>> record = client.com.atproto.repo.get_record(...)
        >>> # using NSID:
        >>> is_record_type(record.value, ids.AppBskyFeedPost)
        >>> # using Python module:
        >>> is_record_type(record.value, models.AppBskyFeedPost)

    Returns:
        :obj:`bool`: Is record or not.
    """
    if isinstance(expected_type, types.ModuleType):
        # for now, all records are defined in the Main class
        if not hasattr(expected_type, 'Main'):
            return False

        expected_type = expected_type.Main._type

    if isinstance(model, DotDict):  # custom (extended) record
        try:
            return expected_type == model[_TYPE_SERVICE_FIELD]
        except ModelFieldNotFoundError:
            return False

    return expected_type == model._type
