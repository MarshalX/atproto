import base64
import binascii
import typing as t
from collections.abc import Mapping

import typing_extensions as te
from pydantic import BeforeValidator, PlainSerializer

_BYTES_KEY = '$bytes'


def _decode_json_bytes(value: object) -> object:
    """Decode the atproto JSON form ``{"$bytes": "<base64>"}``. Raw bytes (from CBOR) pass through."""
    if type(value) is bytes:
        return value
    if not isinstance(value, Mapping) or set(value) != {_BYTES_KEY}:
        return value

    encoded: object = value[_BYTES_KEY]
    if not isinstance(encoded, str):
        return value

    try:
        # the spec drops the padding
        return base64.b64decode(encoded + '=' * (-len(encoded) % 4), validate=True)
    except binascii.Error as e:
        raise ValueError(f'Invalid base64 in {_BYTES_KEY}') from e


def _encode_json_bytes(value: bytes) -> t.Dict[str, str]:
    return {_BYTES_KEY: base64.b64encode(value).decode('ascii').rstrip('=')}


#: Lexicon ``bytes``. JSON carries it as ``{"$bytes": "<base64>"}``; ``model_dump`` keeps the raw bytes.
BytesType = te.Annotated[
    bytes,
    BeforeValidator(_decode_json_bytes),
    PlainSerializer(_encode_json_bytes, when_used='json'),
]
