import typing as t

from atproto_core.cbor import decode_dag
from atproto_core.exceptions import DAGCBORDecodingError, InvalidStarError

Pairs = t.List[t.Tuple[bytes, bytes]]

_MAGIC: t.Final = b'\x2a\x6c\x01\x00'

_CONTROL_END: t.Final = 0x00
_CONTROL_PAIR: t.Final = 0x01

_MAX_VARINT_LEN: t.Final = 9


def _read_byte(data: bytes, position: int) -> int:
    if position >= len(data):
        raise InvalidStarError('Unexpected end of STAR file.')

    return data[position]


def _read_varint(data: bytes, position: int) -> t.Tuple[int, int]:
    value = 0
    for index in range(_MAX_VARINT_LEN):
        byte = _read_byte(data, position + index)
        value |= (byte & 0x7F) << 7 * index
        if byte < 0x80:
            # a final zero byte only pads the varint
            if byte == 0 and index > 0:
                raise InvalidStarError('Invalid STAR file. Varint is not in the shortest form.')

            return value, position + index + 1

    raise InvalidStarError('Invalid STAR file. Varint is too long.')


def _read_frame(data: bytes, position: int, max_length: t.Optional[int]) -> t.Tuple[bytes, int]:
    length, position = _read_varint(data, position)
    if max_length is not None and length > max_length:
        raise InvalidStarError(f'Invalid STAR file. Length {length} exceeds limit of {max_length}.')

    end = position + length
    if end > len(data):
        raise InvalidStarError('Unexpected end of STAR file.')

    return data[position:end], end


def _decode_meta(data: bytes) -> t.Dict[str, t.Any]:
    try:
        meta = decode_dag(data, canonical=True)
    except DAGCBORDecodingError as e:
        raise InvalidStarError('Invalid STAR file. Metadata is not a map in canonical DAG-CBOR.') from e

    if not isinstance(meta.get('$type'), str):
        raise InvalidStarError('Invalid STAR file. Metadata has no $type.')

    return meta


class STAR:
    """STAR file."""

    def __init__(self, meta: t.Dict[str, t.Any], pairs: Pairs) -> None:
        self._meta = meta
        self._pairs = pairs

    @property
    def meta(self) -> t.Dict[str, t.Any]:
        """Get metadata."""
        return self._meta

    @property
    def pairs(self) -> Pairs:
        """Get pairs of key and value in the order of the file."""
        return self._pairs

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        max_meta_length: t.Optional[int] = None,
        max_key_length: t.Optional[int] = None,
        max_value_length: t.Optional[int] = None,
    ) -> 'STAR':
        """Decode STAR file.

        Note:
            You could pass as `data` response of `client.com.atproto.space.get_repo`, for example.
            The meaning of the keys and values is defined by the profile that the `$type` of the metadata names.

        Args:
            data: Content of the STAR file.
            max_meta_length: Max length of the metadata in bytes. Unlimited by default.
            max_key_length: Max length of a key in bytes. Unlimited by default.
            max_value_length: Max length of a value in bytes. Unlimited by default.

        Returns:
            :obj:`atproto_core.star.STAR`: Parsed STAR file.

        Raises:
            :class:`atproto.exceptions.InvalidStarError`: Invalid STAR file.
        """
        if data[: len(_MAGIC)] != _MAGIC:
            raise InvalidStarError('Invalid STAR file. Expected magic bytes.')

        meta_bytes, position = _read_frame(data, len(_MAGIC), max_meta_length)
        meta = _decode_meta(meta_bytes)

        pairs: Pairs = []
        while True:
            control = _read_byte(data, position)
            position += 1
            if control == _CONTROL_END:
                break
            if control != _CONTROL_PAIR:
                raise InvalidStarError(f'Invalid STAR file. Unexpected control byte {control}.')

            key, position = _read_frame(data, position, max_key_length)
            value, position = _read_frame(data, position, max_value_length)
            pairs.append((key, value))

        if position != len(data):
            raise InvalidStarError('Invalid STAR file. Unexpected bytes after the end.')

        return cls(meta=meta, pairs=pairs)
