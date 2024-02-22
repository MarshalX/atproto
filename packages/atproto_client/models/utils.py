import json
import types
import typing as t

import typing_extensions as te
from pydantic import ValidationError

from atproto_client import models
from atproto_client.exceptions import (
    ModelError,
    ModelFieldNotFoundError,
)
from atproto_client.models.base import ModelBase
from atproto_client.models.blob_ref import BlobRef
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.type_conversion import RECORD_TYPE_TO_MODEL_CLASS
from atproto_client.models.unknown_type import UnknownRecordType

if t.TYPE_CHECKING:
    from atproto_client.request import Response

M = t.TypeVar('M')
ModelData: te.TypeAlias = t.Union[
    M, t.Dict[str, t.Any], None
]  # we assume that dict is JSON object. not list or primitive

_TYPE_SERVICE_FIELD = '$type'


def get_or_create(
    model_data: ModelData[M], model: t.Optional[t.Type[M]] = None, *, strict: bool = True
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

    Returns:
        Instance of :obj:`model` or :obj:`None` or
        :obj:`atproto.xrpc_client.models.dot_dict.DotDict` if `strict` is disabled.
    """
    try:
        model_instance = _get_or_create(model_data, model, strict=strict)
        if strict and model_instance is not None and (not model or not isinstance(model_instance, model)):
            raise ModelError(f"Can't properly parse model of type {model}")

        return model_instance
    except Exception as e:  # noqa: BLE001
        if strict or not isinstance(model_data, dict):
            raise e

        return DotDict(model_data)


def _get_or_create(
    model_data: ModelData[M], model: t.Optional[t.Type[M]], *, strict: bool
) -> t.Optional[t.Union[M, UnknownRecordType, DotDict]]:
    if model_data is None:
        return None

    if model is None:
        if not isinstance(model_data, dict):
            return None

        # we are sure that this is dict because of check above
        model_data = t.cast(t.Dict[str, t.Any], model_data)

        # resolve a record model by type and try to deserialize
        record_type: t.Any = model_data.get(_TYPE_SERVICE_FIELD)
        if record_type not in RECORD_TYPE_TO_MODEL_CLASS:
            return None

        # now we are sure that this is str because it's in RECORD_TYPE_TO_MODEL_CLASS
        record_type = t.cast(str, record_type)

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
        return t.cast(M, response.success)
    if model is bytes:
        return t.cast(M, response.content)

    if not isinstance(response.content, dict):
        raise ModelError("Can't properly parse response model because JSON is expected in response")

    # casting to M because of enabled strict mode
    return t.cast(M, get_or_create(response.content, model, strict=True))


def get_model_as_dict(model: t.Union[DotDict, BlobRef, ModelBase]) -> t.Dict[str, t.Any]:
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
        >>> from atproto_client.models import ids, is_record_type
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
        # for now, all records are defined in the Record class
        # TODO(MarshalX): remove backward compatibility for Main
        if not hasattr(expected_type, 'Main') or not hasattr(expected_type, 'Record'):
            return False

        if hasattr(expected_type, 'Main'):
            expected_type = expected_type.Main.model_fields['py_type'].default

        if hasattr(expected_type, 'Record'):
            expected_type = expected_type.Record.model_fields['py_type'].default

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
