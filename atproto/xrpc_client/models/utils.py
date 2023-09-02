import json
import types
import typing as t

import typing_extensions as te
from pydantic import ValidationError

from atproto.exceptions import (
    ModelError,
    ModelFieldNotFoundError,
)
from atproto.xrpc_client import models
from atproto.xrpc_client.models.base import ModelBase
from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models.dot_dict import DotDict
from atproto.xrpc_client.models.type_conversion import RECORD_TYPE_TO_MODEL_CLASS
from atproto.xrpc_client.models.unknown_type import UnknownRecordType

if t.TYPE_CHECKING:
    from atproto.xrpc_client.request import Response

M = t.TypeVar('M')
ModelData: te.TypeAlias = t.Union[M, dict, None]

_TYPE_SERVICE_FIELD = '$type'


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
        :obj:`atproto.xrpc_client.models.dot_dict.DotDict` if `strict` is disabled.
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
        return model(**model_data)
    except ValidationError as e:
        raise ModelError(str(e)) from e


def get_response_model(response: 'Response', model: t.Type[M]) -> M:
    if model is bool:
        # Could not be False? Because the exception with errors will be raised from the server
        return response.success

    # return is optional if response.content is None, but doesn't occur in practice
    return get_or_create(response.content, model)


def get_model_as_dict(model: t.Union[DotDict, BlobRef, ModelBase]) -> dict:
    if isinstance(model, DotDict):
        return model.to_dict()

    return model.model_dump(exclude_none=True, by_alias=True)


def get_model_as_json(model: t.Union[DotDict, BlobRef, ModelBase]) -> str:
    if isinstance(model, DotDict):
        return json.dumps(get_model_as_dict(model))

    return model.model_dump_json(exclude_none=True, by_alias=True)


def is_json(json_data: t.Union[str, bytes]) -> bool:
    if isinstance(json_data, bytes):
        json_data.decode('UTF-8')

    try:
        json.loads(json_data)
        return True
    except:  # noqa
        return False


def is_record_type(model: t.Union[ModelBase, DotDict], expected_type: t.Union[str, types.ModuleType]) -> bool:
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

        expected_type = expected_type.Main.model_fields['py_type'].default

    if isinstance(model, DotDict):  # custom (extended) record
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
        >>> client.like(create_strong_ref(response))
        >>> client.repost(create_strong_ref(response))

    Returns:
        :obj:`atproto.xrpc_client.models.com.atproto.repo.strong_ref.Main`: Strong ref.
    """
    if hasattr(model, 'cid') and hasattr(model, 'uri'):
        return models.ComAtprotoRepoStrongRef.Main(cid=model.cid, uri=model.uri)

    raise ModelError('Could not create strong ref from model')
