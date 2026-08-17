import struct
import typing as t

import zstandard

from atproto_jetstream.exceptions import JetstreamDecodingError

#: Magic of a zstd dictionary blob (RFC 8878, section 5).
_DICTIONARY_MAGIC = 0xEC30A437
_DICTIONARY_HEADER_LEN = 8


def parse_dictionary_id(blob: bytes) -> int:
    """Read the dictionary ID that the server expects on the `zstdDictionary` param.

    Args:
        blob: Raw zstd dictionary.

    Returns:
        :obj:`int`: Dictionary ID.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Not a zstd dictionary.
    """
    if len(blob) < _DICTIONARY_HEADER_LEN:
        raise JetstreamDecodingError('Zstd dictionary is too short')

    magic, dictionary_id = struct.unpack('<II', blob[:_DICTIONARY_HEADER_LEN])
    if magic != _DICTIONARY_MAGIC:
        raise JetstreamDecodingError('Not a zstd dictionary')

    return dictionary_id


class ZstdDecompression:
    """Dictionary-seeded zstd decompression of the live tail.

    The decompression context is built once per dictionary and reused for every frame.
    """

    def __init__(self, max_output_size: int) -> None:
        self._max_output_size = max_output_size
        self._dictionary_id: t.Optional[int] = None
        self._decompressor: t.Optional[zstandard.ZstdDecompressor] = None

    @property
    def dictionary_id(self) -> t.Optional[int]:
        """:obj:`int`: ID of the loaded dictionary, or :obj:`None` if none is loaded."""
        return self._dictionary_id

    def load(self, blob: bytes) -> int:
        """Load a dictionary and build the decompression context.

        Args:
            blob: Raw zstd dictionary.

        Returns:
            :obj:`int`: ID of the loaded dictionary.

        Raises:
            :class:`atproto.exceptions.JetstreamDecodingError`: Not a zstd dictionary.
        """
        dictionary_id = parse_dictionary_id(blob)

        self._dictionary_id = dictionary_id
        self._decompressor = zstandard.ZstdDecompressor(dict_data=zstandard.ZstdCompressionDict(blob))

        return dictionary_id

    def unload(self) -> None:
        """Drop the dictionary and the context."""
        self._dictionary_id = None
        self._decompressor = None

    def decompress(self, data: bytes) -> bytes:
        """Decompress one frame.

        Args:
            data: One zstd frame.

        Returns:
            :obj:`bytes`: Decompressed frame.

        Raises:
            :class:`atproto.exceptions.JetstreamDecodingError`: Undecodable or oversized frame.
        """
        if self._decompressor is None:
            raise JetstreamDecodingError('Zstd dictionary is not loaded')

        try:
            # max_output_size caps decompression; the read limit bounds only the compressed bytes
            return self._decompressor.decompress(data, max_output_size=self._max_output_size)
        except zstandard.ZstdError as e:
            raise JetstreamDecodingError('Could not decompress the frame') from e
