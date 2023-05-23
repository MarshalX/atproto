from io import BytesIO
from typing import List, Union

import dag_cbor as _dag_cbor

DagCborData = Union[bytes, bytearray, BytesIO]


class _BytesReadCounter:
    _num_bytes_read = 0

    def __call__(self, _, num_bytes_read: int):
        self._num_bytes_read += num_bytes_read

    def __int__(self) -> int:
        return self._num_bytes_read


def decode_dag(data: DagCborData, *, allow_concat=False, callback=None) -> _dag_cbor.IPLDKind:
    """Decodes and returns a single data item from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.
        allow_concat: Allow partial stream decoding.
        callback: Callback on every time an item is decoded.

    Returns:
        :obj:`dag_cbor.IPLDKind`: Decoded DAG-CBOR.
    """
    return _dag_cbor.decode(data, allow_concat=allow_concat, callback=callback)


def decode_dag_multi(data: DagCborData) -> List[_dag_cbor.IPLDKind]:
    """Decodes and returns many data items from the given data, with the DAG-CBOR codec.

    Args:
        data: The stream of bytes or bytes with DAG-CBOR data.

    Returns:
        :obj:`list` of :obj:`dag_cbor.IPLDKind`: Decoded DAG-CBOR.
    """

    if not isinstance(data, BytesIO):
        data = BytesIO(data)

    data_size = data.getbuffer().nbytes

    data_parts = []
    if data_size == 0:
        return data_parts

    bytes_read_counter = _BytesReadCounter()
    while int(bytes_read_counter) != data_size:
        decoded_part = decode_dag(data, allow_concat=True, callback=bytes_read_counter)
        data_parts.append(decoded_part)

    return data_parts
