from typing import Type, TypeVar

from dacite import exceptions, from_dict
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

M = TypeVar('M')


def get_or_create_model(model_data: Union[dict, M], model: Type[M]) -> Optional[M]:
    if model_data is None:
        return None

    if isinstance(model_data, model):
        return model_data

    try:
        # validate unexpected fields
        model(**model_data)

        return from_dict(model, model_data)
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
