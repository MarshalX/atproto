from typing import List

import libipld

from atproto_core.exceptions import DAGCBORDecodingError


def decode_dag(data: bytes) -> dict:
    """Decodes and returns a single data item from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.

    Returns:
        :obj:`dict`: Decoded DAG-CBOR.
    """

    try:
        return libipld.decode_dag_cbor(data)
    except Exception as e:  # noqa: BLE001
        raise DAGCBORDecodingError from e


def decode_dag_multi(data: bytes) -> List[dict]:
    """Decodes and returns many data items from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.

    Returns:
        :obj:`list` of :obj:`dict`: Decoded DAG-CBOR.
    """
    return libipld.decode_dag_cbor_multi(data)
