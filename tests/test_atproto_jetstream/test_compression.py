import struct
import sys

import pytest
import zstandard
from atproto_jetstream import compression
from atproto_jetstream.compression import ZstdDecompression, decompress_frame
from atproto_jetstream.exceptions import JetstreamDecodingError

from .conftest import DICTIONARIES

_DICTIONARY = DICTIONARIES['current']


def _decompression(max_output_size: int) -> ZstdDecompression:
    decompression = ZstdDecompression(max_output_size)
    decompression.load(_DICTIONARY.as_bytes())
    return decompression


def _frame(data: bytes, write_content_size: bool = True) -> bytes:
    return zstandard.ZstdCompressor(dict_data=_DICTIONARY, write_content_size=write_content_size).compress(data)


@pytest.mark.parametrize('write_content_size', [True, False])
def test_frame_within_limit_decompresses(write_content_size: bool) -> None:
    assert _decompression(4096).decompress(_frame(b'x' * 4096, write_content_size)) == b'x' * 4096


@pytest.mark.parametrize('write_content_size', [True, False])
def test_oversized_frame_is_rejected(write_content_size: bool) -> None:
    with pytest.raises(JetstreamDecodingError):
        _decompression(1024).decompress(_frame(b'x' * 4096, write_content_size))


@pytest.mark.parametrize(
    'data', [b'\x28\xb5\x2f\xfd' + b'\xff' * 32, _frame(b'x' * 4096)[:-4]], ids=['garbage', 'truncated']
)
def test_undecodable_frame_is_rejected(data: bytes) -> None:
    with pytest.raises(JetstreamDecodingError):
        _decompression(1 << 20).decompress(data)


def test_corrupt_dictionary_is_rejected() -> None:
    blob = struct.pack('<II', 0xEC30A437, 1234) + b'\xff' * 200

    with pytest.raises(JetstreamDecodingError):
        ZstdDecompression(1024).load(blob)


@pytest.mark.parametrize('write_content_size', [True, False])
def test_frame_without_dictionary(write_content_size: bool) -> None:
    frame = zstandard.ZstdCompressor(write_content_size=write_content_size).compress(b'x' * 4096)

    assert decompress_frame(frame, 4096) == b'x' * 4096
    with pytest.raises(JetstreamDecodingError):
        decompress_frame(frame, 1024)


def test_backend_falls_back_to_stdlib_without_zstandard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.undo()  # drop the autouse backend override
    monkeypatch.setitem(sys.modules, 'zstandard', None)
    compression._select_backend.cache_clear()
    try:
        if sys.version_info >= (3, 14):
            assert compression._select_backend() is compression._StdlibDecompressor
        else:
            assert not compression.is_available()
            with pytest.raises(ImportError, match='atproto\\[zstd\\]'):
                decompress_frame(b'', 1024)
    finally:
        compression._select_backend.cache_clear()


def test_backend_prefers_zstandard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.undo()
    compression._select_backend.cache_clear()

    assert compression._select_backend() is compression._ZstandardDecompressor
