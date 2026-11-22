import base64
import hashlib
import re
import typing as t

import libipld
from atproto_core.cbor import decode_dag, encode_dag
from atproto_core.cid import CID
from atproto_core.exceptions import DAGCBORDecodingError, DAGCBOREncodingError

DAG_CBOR_CODEC: t.Final = 0x71
RAW_CODEC: t.Final = 0x55

_CID_VERSION: t.Final = 1
_SHA2_256_CODE: t.Final = 0x12
_SHA2_256_SIZE: t.Final = 32

# no CID is longer, and the decoders of base58btc and base36 take quadratic time
_MAX_CID_LENGTH: t.Final = 128

_LINK_KEY: t.Final = '$link'
# hosts read a link in base32 and base36 of lower case and in base58btc, which is the form of CIDv0 without the prefix
_LINK_REGEX: t.Final = re.compile(r'b[a-z2-7]+=*|k[0-9a-z]+|z[1-9A-HJ-NP-Za-km-z]+|Qm[1-9A-HJ-NP-Za-km-z]{44}')
_BYTES_KEY: t.Final = '$bytes'

_MAX_SAFE_INTEGER: t.Final = 2**53 - 1


def _decode_cid(cid: str) -> t.Optional[CID]:
    if len(cid) > _MAX_CID_LENGTH:
        return None

    try:
        return CID.decode(cid)
    except ValueError:
        return None


def _encode_cid(codec: int, digest: bytes) -> str:
    return libipld.encode_cid(bytes([_CID_VERSION, codec, _SHA2_256_CODE, _SHA2_256_SIZE]) + digest)


def _decode_link(link: str) -> t.Optional[CID]:
    """Decode a CID from a string, if a host reads a link from this string as well."""
    if len(link) > _MAX_CID_LENGTH or _LINK_REGEX.fullmatch(link) is None:
        return None

    # hosts take base32 with the padding
    return _decode_cid(link.rstrip('='))


def _parse_link(value: t.Dict[str, t.Any]) -> t.Optional[CID]:
    link = value.get(_LINK_KEY)
    if len(value) != 1 or not isinstance(link, str):
        return None

    return _decode_link(link)


def _parse_bytes(value: t.Dict[str, t.Any]) -> t.Optional[bytes]:
    encoded = value.get(_BYTES_KEY)
    if len(value) != 1 or not isinstance(encoded, str):
        return None

    try:
        # the spec drops the padding
        return base64.b64decode(encoded + '=' * (-len(encoded) % 4), validate=True)
    except ValueError:
        return None


def _convert_float(value: float) -> int:
    # JSON does not tell an integer from a float of the same value
    if not value.is_integer() or abs(value) > _MAX_SAFE_INTEGER:
        raise ValueError(f'Number {value} is not a safe integer')

    return int(value)


def _convert_map(value: t.Dict[str, t.Any]) -> t.Any:
    link = _parse_link(value)
    if link is not None:
        return link

    data = _parse_bytes(value)
    if data is not None:
        return data

    return {key: _convert(item) for key, item in value.items()}


def _convert(value: t.Any) -> t.Any:
    if isinstance(value, dict):
        return _convert_map(value)
    if isinstance(value, list):
        return [_convert(item) for item in t.cast('t.List[t.Any]', value)]
    if isinstance(value, float):
        return _convert_float(value)

    return value


def encode_json_value(value: t.Any) -> bytes:
    """Encode a value given in the JSON form of the data model with the DAG-CBOR codec.

    An object with the only key ``$link`` is a link and an object with the only key ``$bytes`` is a byte string.
    Such an object stays a map when it holds no CID in a form that hosts read a link in, or no base64.

    Raises:
        :class:`ValueError`: The value has no DAG-CBOR form.
    """
    try:
        return encode_dag(_convert(value))
    except (DAGCBOREncodingError, RecursionError) as e:
        raise ValueError('Value has no DAG-CBOR form') from e


def json_to_ipld(value: t.Any) -> t.Dict[str, t.Any]:
    """Convert a map given in the JSON form of the data model to the form that DAG-CBOR decodes to.

    Raises:
        :class:`ValueError`: The value is not a map or has no DAG-CBOR form.
    """
    try:
        return decode_dag(encode_json_value(value))
    except DAGCBORDecodingError as e:
        raise ValueError('Value is not a DAG-CBOR map') from e


def get_record_cid(data: bytes) -> str:
    """Get the CID of a record from its DAG-CBOR bytes."""
    return _encode_cid(DAG_CBOR_CODEC, hashlib.sha256(data).digest())


def get_blob_cid(data: bytes) -> str:
    """Get the CID of a blob from its content."""
    return _encode_cid(RAW_CODEC, hashlib.sha256(data).digest())


def is_sha256_cid(cid: str, codec: int) -> bool:
    """Tell whether the string is the canonical form of a CIDv1 with the given codec and a SHA-256 digest."""
    decoded = _decode_cid(cid)
    if decoded is None:
        return False

    multihash = decoded.hash

    return (
        decoded.version == _CID_VERSION
        and decoded.codec == codec
        and multihash.code == _SHA2_256_CODE
        and multihash.size == _SHA2_256_SIZE
        and cid == _encode_cid(codec, multihash.digest)
    )
