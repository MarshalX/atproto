import dataclasses
import json
from typing import Type, TypeVar

from dacite import Config, exceptions, from_dict
from exceptions import (
    MissingValueError,
    ModelError,
    ModelFieldError,
    UnexpectedFieldError,
    WrongTypeError,
)
from xrpc_client.models.data import *
from xrpc_client.models.defs import *
from xrpc_client.models.params import *
from xrpc_client.models.records import *
from xrpc_client.models.responses import *
from xrpc_client.request import Response

M = TypeVar('M')

_DACITE_CONFIG = Config(type_hooks={BlobRef: lambda ref: BlobRef.from_dict(ref)})


def get_or_create_model(model_data: Union[dict], model: Type[M]) -> Optional[M]:
    if model_data is None:
        return None

    if isinstance(model_data, model):
        return model_data

    try:
        # validate unexpected fields
        model(**model_data)

        return from_dict(model, model_data, config=_DACITE_CONFIG)
    except TypeError as e:
        msg = str(e).replace('__init__()', model.__name__)
        raise UnexpectedFieldError(msg)
    except exceptions.MissingValueError as e:
        raise MissingValueError(str(e))
    except exceptions.WrongTypeError as e:
        raise WrongTypeError(str(e))
    except exceptions.DaciteFieldError as e:
        raise ModelFieldError(str(e))
    except exceptions.DaciteError as e:
        raise ModelError(str(e))


def get_response_model(response: Response, model: Type[M]) -> Optional[M]:
    if model is int:
        return response.status_code

    return get_or_create_model(response.content, model)


def _handle_dict_key(key: str) -> str:
    if key == '_type':  # special SDK's name to resolve issues with $ symbol in Python
        return '$type'

    return key


def _handle_dict_value(ref: Any) -> dict:
    # TODO(MarshalX): add CID?
    if isinstance(ref, BlobRef):
        return ref.to_dict()

    return ref


def _model_as_dict_factory(value):
    # exclude None values and process keys and values
    return {_handle_dict_key(k): _handle_dict_value(v) for k, v in value if v is not None}


def get_model_as_dict(model) -> dict:
    if model == BlobRef:
        return model.to_dict()

    if not dataclasses.is_dataclass(model):
        raise ModelError('Invalid model')

    return dataclasses.asdict(model, dict_factory=_model_as_dict_factory)


def get_model_as_json(model) -> str:
    return json.dumps(get_model_as_dict(model))


def is_json(json_data: Union[str, bytes]):
    if isinstance(json_data, bytes):
        json_data.decode('UTF-8')

    try:
        json.loads(json_data)
        return True
    except Exception:  # noqa
        return False
