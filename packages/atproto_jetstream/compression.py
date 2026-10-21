import functools
import sys
import typing as t

from atproto_jetstream.exceptions import JetstreamDecodingError

#: Magic of a zstd dictionary blob (RFC 8878, section 5).
_DICTIONARY_MAGIC = 0xEC30A437
_DICTIONARY_HEADER_LEN = 8

_NO_BACKEND_MESSAGE = 'Zstd decompression needs Python 3.14+ or the zstandard package: pip install "atproto[zstd]"'


class _Decompressor(t.Protocol):
    def decompress(self, data: bytes, max_output_size: int) -> bytes: ...


class _ZstandardDecompressor:
    """Decompression with the `zstandard` package. Not safe for concurrent use."""

    def __init__(self, dictionary: t.Optional[bytes]) -> None:
        import zstandard

        self._zstandard = zstandard
        dict_data = zstandard.ZstdCompressionDict(dictionary) if dictionary is not None else None
        try:
            self._context = zstandard.ZstdDecompressor(dict_data=dict_data)
        except zstandard.ZstdError as e:
            raise JetstreamDecodingError('Invalid zstd dictionary') from e

    def decompress(self, data: bytes, max_output_size: int) -> bytes:
        try:
            # zstandard applies max_output_size only to frames that do not declare their content size
            if self._zstandard.frame_content_size(data) > max_output_size:
                raise JetstreamDecodingError('Frame exceeds the size limit')

            return self._context.decompress(data, max_output_size=max_output_size)
        except self._zstandard.ZstdError as e:
            raise JetstreamDecodingError('Could not decompress the frame') from e


if sys.version_info >= (3, 14):

    class _StdlibDecompressor:
        """Decompression with the standard library `compression.zstd` module."""

        def __init__(self, dictionary: t.Optional[bytes]) -> None:
            from compression import zstd

            self._zstd = zstd
            self._dictionary = zstd.ZstdDict(dictionary) if dictionary is not None else None
            try:
                # a context per frame, as stdlib contexts are single-use; this one validates the dictionary
                zstd.ZstdDecompressor(zstd_dict=self._dictionary)
            except zstd.ZstdError as e:
                raise JetstreamDecodingError('Invalid zstd dictionary') from e

        def decompress(self, data: bytes, max_output_size: int) -> bytes:
            context = self._zstd.ZstdDecompressor(zstd_dict=self._dictionary)
            try:
                output = context.decompress(data, max_length=max_output_size)
            except self._zstd.ZstdError as e:
                raise JetstreamDecodingError('Could not decompress the frame') from e

            if not context.eof:
                raise JetstreamDecodingError('Frame is truncated or exceeds the size limit')

            return output


@functools.cache
def _select_backend() -> t.Optional[t.Callable[[t.Optional[bytes]], _Decompressor]]:
    """Prefer `zstandard`, which is faster; fall back to the standard library on Python 3.14+."""
    try:
        import zstandard  # noqa: F401
    except ImportError:
        pass
    else:
        return _ZstandardDecompressor

    if sys.version_info >= (3, 14):
        return _StdlibDecompressor

    return None


def is_available() -> bool:
    """Whether zstd decompression is available."""
    return _select_backend() is not None


def _new_decompressor(dictionary: t.Optional[bytes] = None) -> _Decompressor:
    backend = _select_backend()
    if backend is None:
        raise ImportError(_NO_BACKEND_MESSAGE)

    return backend(dictionary)


def decompress_frame(data: bytes, max_output_size: int) -> bytes:
    """Decompress one zstd frame that does not use a dictionary.

    Args:
        data: One zstd frame.
        max_output_size: Output size limit.

    Returns:
        :obj:`bytes`: Decompressed frame.

    Raises:
        :class:`atproto.exceptions.JetstreamDecodingError`: Undecodable or oversized frame.
        :class:`ImportError`: No zstd backend is available.
    """
    return _new_decompressor().decompress(data, max_output_size)


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

    magic = int.from_bytes(blob[:4], 'little')
    dictionary_id = int.from_bytes(blob[4:_DICTIONARY_HEADER_LEN], 'little')
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
        self._decompressor: t.Optional[_Decompressor] = None

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
            :class:`ImportError`: No zstd backend is available.
        """
        dictionary_id = parse_dictionary_id(blob)

        self._decompressor = _new_decompressor(blob)
        self._dictionary_id = dictionary_id

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

        return self._decompressor.decompress(data, self._max_output_size)
