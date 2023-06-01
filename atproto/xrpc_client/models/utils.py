import dataclasses
import json
import typing as t
from enum import Enum

import typing_extensions as te
from dacite import Config, exceptions, from_dict

from atproto.cid import CID
from atproto.exceptions import (
    MissingValueError,
    ModelError,
    ModelFieldError,
    UnexpectedFieldError,
    WrongTypeError,
)
from atproto.xrpc_client.models.base import ModelBase, RecordModelBase
from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models.type_conversion import RECORD_TYPE_TO_MODEL_CLASS

if t.TYPE_CHECKING:
    from atproto.xrpc_client.request import Response

M = t.TypeVar('M')
ModelData: te.TypeAlias = t.Union[M, dict, None]


def _record_model_type_hook(data: dict) -> RecordModelBase:
    # used for inner Record types
    record_type = data.pop('$type')
    return get_or_create_model(data, RECORD_TYPE_TO_MODEL_CLASS[record_type])


def _decode_cid_hook(ref: t.Union[CID, str]) -> CID:
    if isinstance(ref, CID):
        return ref

    return CID.decode(ref)


_TYPE_HOOKS = {
    BlobRef: lambda ref: BlobRef.from_dict(ref),
    CID: _decode_cid_hook,
    RecordModelBase: _record_model_type_hook,
}
_DACITE_CONFIG = Config(cast=[Enum], type_hooks=_TYPE_HOOKS)


def get_or_create(
    model_data: ModelData, model: t.Type[M] = None, *, strict: bool = True
) -> t.Optional[t.Union[M, dict]]:
    """Get model instance from raw data.

    Note:
        The record could have custom fields and be custom at all. For example, custom bsky clients add a "via" field
        to indicate that it was posted using not official client. Such custom types can't be decoded into proper models.
        You should work with it as with dict. By default, the method raises an exception on custom models.
        To fallback to dict type disable strict mode using the argument.

    Note:
        Auto-resolve of model works only with Record type for now.

    Args:
        model_data: Raw data.
        model: Class of the model or any another type. If None will be resolved automatically.
        strict: Fallback to raw data if can't properly parse.

    Returns:
        Instance of :obj:`model` or :obj:`None` or :obj:`dict` if `strict` is disabled.
    """
    try:
        return _get_or_create(model_data, model, strict=strict)
    except Exception as e:  # noqa: BLE001
        if strict:
            raise e

        return model_data


def _get_or_create(model_data: ModelData, model: t.Type[M], *, strict: bool) -> t.Optional[t.Union[M, dict]]:
    if model_data is None:
        return None

    if model is None:
        # resolve model by $type and try to parse
        # resolves only Records
        record_type = model_data.pop('$type')
        if not record_type or record_type not in RECORD_TYPE_TO_MODEL_CLASS:
            return None

        return get_or_create(model_data, RECORD_TYPE_TO_MODEL_CLASS[record_type], strict=strict)

    if isinstance(model_data, model):
        return model_data

    try:
        # validate unexpected fields
        model(**model_data)

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


def get_or_create_model(model_data: ModelData, model: t.Type[M]) -> t.Optional[M]:
    model_instance = get_or_create(model_data, model)
    if model_instance is not None and not isinstance(model_instance, model):
        raise ModelError(f"Can't properly parse model of type {model}")

    return model_instance


def get_response_model(response: 'Response', model: t.Type[M]) -> M:
    if model is bool:
        # Could not be False? Because the exception with errors will be raised from the server
        return response.success

    # return is optional if response.content is None, but doesn't occur in practice
    return get_or_create_model(response.content, model)


def _handle_dict_key(key: str) -> str:
    if key == '_type':  # System field. Replaced to original $ symbol because it is not allowed in Python.
        return '$type'

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
    if model == BlobRef:
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


def is_record_type(model: t.Union[ModelBase, dict], types_module) -> bool:
    if isinstance(model, RecordModelBase) and hasattr(types_module, 'Main'):
        # for now records in Main. could be broken late
        if isinstance(model, dict):  # custom record
            return types_module.Main._type == model.get('$type')

        return types_module.Main._type == model._type

    return False
