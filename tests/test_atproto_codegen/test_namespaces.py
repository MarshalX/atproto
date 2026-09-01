from pathlib import Path

from atproto_codegen.config import CodegenConfig
from atproto_codegen.namespaces.generator import generate_namespaces

from .conftest import CUSTOM_LEXICON_DIR

_SDK_CLIENT_DIR = CodegenConfig().output_dir.joinpath('client')


def test_output_dir_override_leaves_the_sdk_client_alone(tmp_path: Path) -> None:
    """Namespaces written elsewhere must not regenerate ``ClientRaw`` from them."""
    raw_clients = {path: path.read_bytes() for path in (_SDK_CLIENT_DIR / 'raw.py', _SDK_CLIENT_DIR / 'async_raw.py')}

    try:
        generate_namespaces(CodegenConfig(emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,)), tmp_path)

        assert tmp_path.joinpath('sync_ns.py').is_file()
        assert tmp_path.joinpath('async_ns.py').is_file()
        assert {path: path.read_bytes() for path in raw_clients} == raw_clients
    finally:
        for path, content in raw_clients.items():
            path.write_bytes(content)
