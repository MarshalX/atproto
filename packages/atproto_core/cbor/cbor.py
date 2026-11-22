import typing as t

import libipld

from atproto_core.exceptions import DAGCBORDecodingError, DAGCBOREncodingError


def decode_dag(data: bytes, *, canonical: bool = False) -> t.Dict[str, t.Any]:
    """Decode and returns a single data item from the given data, with the DAG-CBOR codec.

    Note:
        A link decodes to :obj:`atproto_core.cid.CID`.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.
        canonical: Also reject data that is not in the canonical form, the only encoding of its value
            that DAG-CBOR allows.

    Returns:
        :obj:`dict`: Decoded DAG-CBOR.
    """
    try:
        decoded = libipld.decode_dag_cbor(data, canonical=canonical)
    except Exception as e:
        raise DAGCBORDecodingError from e

    if not isinstance(decoded, dict):
        raise DAGCBORDecodingError('Expected a DAG-CBOR map at the top level.')

    return decoded


def decode_dag_multi(data: bytes, *, canonical: bool = False) -> t.List[t.Dict[str, t.Any]]:
    """Decode and returns many data items from the given data, with the DAG-CBOR codec.

    Note:
        A link decodes to :obj:`atproto_core.cid.CID`.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.
        canonical: Also reject data items that are not in the canonical form.

    Returns:
        :obj:`list` of :obj:`dict`: Decoded DAG-CBOR.
    """
    try:
        return libipld.decode_dag_cbor_multi(data, canonical=canonical)
    except Exception as e:
        raise DAGCBORDecodingError from e


def encode_dag(value: t.Any) -> bytes:
    """Encode the given value with the DAG-CBOR codec, in the canonical form.

    Note:
        A :obj:`atproto_core.cid.CID` encodes as a link, :obj:`bytes` as a byte string
        and a :obj:`tuple` as an array.

    Args:
        value: The value to encode.

    Returns:
        :obj:`bytes`: Encoded DAG-CBOR.

    Raises:
        :class:`atproto.exceptions.DAGCBOREncodingError`: The value has no DAG-CBOR form.
    """
    try:
        return libipld.encode_dag_cbor(value)
    except Exception as e:
        raise DAGCBOREncodingError from e
