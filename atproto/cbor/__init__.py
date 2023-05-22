from io import BytesIO
from typing import List, Union

import dag_cbor as _dag_cbor

CborData = Union[bytes, bytearray, BytesIO]


class _BytesReadCounter:
    _num_bytes_read = 0

    def __call__(self, _, num_bytes_read: int):
        self._num_bytes_read += num_bytes_read

    def __int__(self) -> int:
        return self._num_bytes_read


def decode(data: CborData, *, allow_concat=False, callback=None):
    return _dag_cbor.decode(data, allow_concat=allow_concat, callback=callback)


def decode_multi(data: CborData) -> List[dict]:
    if not isinstance(data, BytesIO):
        data = BytesIO(data)

    data_size = data.getbuffer().nbytes

    data_parts = []
    if data_size == 0:
        return data_parts

    bytes_read_counter = _BytesReadCounter()
    while int(bytes_read_counter) != data_size:
        decoded_part = decode(data, allow_concat=True, callback=bytes_read_counter)
        data_parts.append(decoded_part)

    return data_parts
