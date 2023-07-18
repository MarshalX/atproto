from io import BytesIO
from typing import Dict, List, Union

import dag_cbor as _dag_cbor
from dag_cbor.decoding import CBORDecodingError as _CBORDecodingError

from atproto.exceptions import CBORDecodingError, DAGCBORDecodingError

DagCborData = Union[bytes, bytearray, BytesIO]


class _BytesReadCounter:
    _num_bytes_read = 0

    def __call__(self, _, num_bytes_read: int) -> None:
        self._num_bytes_read += num_bytes_read

    def __int__(self) -> int:
        return self._num_bytes_read


def decode_dag(data: DagCborData, *, allow_concat: bool = False, callback=None) -> Dict[str, _dag_cbor.IPLDKind]:
    """Decodes and returns a single data item from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.
        allow_concat: Allow partial stream decoding.
        callback: Callback on every time an item is decoded.

    Returns:
        :obj:`dag_cbor.IPLDKind`: Decoded DAG-CBOR.
    """
    try:
        decoded_data = _dag_cbor.decode(data, allow_concat=allow_concat, callback=callback)
        if isinstance(decoded_data, dict):
            return decoded_data
        raise DAGCBORDecodingError(f'Invalid DAG-CBOR data. Expected dict instead of {type(decoded_data).__name__}')
    except _CBORDecodingError as e:
        raise CBORDecodingError from e
    except Exception as e:  # noqa: BLE001
        raise DAGCBORDecodingError from e


def decode_dag_multi(data: DagCborData) -> List[Dict[str, _dag_cbor.IPLDKind]]:
    """Decodes and returns many data items from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.

    Returns:
        :obj:`list` of :obj:`dag_cbor.IPLDKind`: Decoded DAG-CBOR.
    """

    if not isinstance(data, BytesIO):
        data = BytesIO(data)

    data_size = data.getbuffer().nbytes

    data_parts: List[Dict[str, _dag_cbor.IPLDKind]] = []
    if data_size == 0:
        return data_parts

    bytes_read_counter = _BytesReadCounter()
    while int(bytes_read_counter) != data_size:
        decoded_part = decode_dag(data, allow_concat=True, callback=bytes_read_counter)
        data_parts.append(decoded_part)

    return data_parts
