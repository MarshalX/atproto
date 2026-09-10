import importlib
import json
import shutil
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_cli import atproto_cli
from atproto_cli import cli as cli_module
from atproto_codegen.config import CodegenConfig
from atproto_codegen.exceptions import LexiconsNotFoundError, RuffNotFoundError, UnresolvedReferenceError
from atproto_codegen.models.generator import generate_models
from click.testing import CliRunner

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()

_QUERY_LEXICON = {
    'lexicon': 1,
    'id': 'com.example.getThing',
    'defs': {
        'main': {
            'type': 'query',
            'output': {
                'encoding': 'application/json',
                'schema': {'type': 'object', 'required': ['name'], 'properties': {'name': {'type': 'string'}}},
            },
        }
    },
}


def _invoke(lexicon_dir: Path, output_dir: Path, package: str) -> t.Any:
    return CliRunner().invoke(
        atproto_cli,
        ['gen', '--lexicon-dir', str(lexicon_dir), 'custom', '--output-dir', str(output_dir), '--package', package],
    )


def _write_lexicon(lexicon_dir: Path, lexicon: t.Dict[str, t.Any]) -> None:
    lexicon_dir.mkdir(parents=True, exist_ok=True)
    lexicon_dir.joinpath(f'{lexicon["id"]}.json').write_text(json.dumps(lexicon))


def test_missing_ruff_fails_before_anything_is_written(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_ruff() -> str:
        raise RuffNotFoundError('Ruff is required. Install it with `pip install ruff`.')

    monkeypatch.setattr(cli_module, 'find_ruff', no_ruff)
    output_dir = tmp_path.joinpath('pkg')

    result = _invoke(CUSTOM_LEXICON_DIR, output_dir, 'pkg')

    assert result.exit_code != 0
    assert 'pip install ruff' in result.output
    assert 'Traceback' not in result.output
    assert not output_dir.exists()


def test_empty_lexicon_dir_is_reported(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    lexicon_dir.mkdir()
    output_dir = tmp_path.joinpath('pkg')

    result = _invoke(lexicon_dir, output_dir, 'pkg')

    assert result.exit_code != 0
    assert 'No .json lexicons found' in result.output
    assert 'Traceback' not in result.output
    assert not output_dir.joinpath('models').exists()


def test_missing_lexicon_dir_raises_instead_of_generating_nothing(tmp_path: Path) -> None:
    config = CodegenConfig(emit_lexicon_dirs=(tmp_path.joinpath('nope'),), output_dir=tmp_path.joinpath('pkg'))

    with pytest.raises(LexiconsNotFoundError, match='does not exist'):
        generate_models(config)

    assert not tmp_path.joinpath('pkg').exists()


def test_reference_to_unknown_lexicon_is_reported(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    _write_lexicon(
        lexicon_dir,
        {
            'lexicon': 1,
            'id': 'com.example.thing',
            'defs': {
                'main': {
                    'type': 'record',
                    'key': 'tid',
                    'record': {
                        'type': 'object',
                        'properties': {'ref': {'type': 'ref', 'ref': 'com.other.unknown#view'}},
                    },
                }
            },
        },
    )
    config = CodegenConfig(emit_lexicon_dirs=(lexicon_dir,), output_dir=tmp_path.joinpath('pkg'), package='pkg')

    with pytest.raises(UnresolvedReferenceError, match=r"'com.other.unknown' \(model 'View'\)"):
        generate_models(config)

    result = _invoke(lexicon_dir, tmp_path.joinpath('cli_pkg'), 'cli_pkg')

    assert result.exit_code != 0
    assert 'com.other.unknown' in result.output
    assert 'Traceback' not in result.output


def test_rerun_drops_modules_of_removed_lexicons(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    shutil.copytree(CUSTOM_LEXICON_DIR, lexicon_dir)
    _write_lexicon(lexicon_dir, _QUERY_LEXICON)
    output_dir = tmp_path.joinpath('pkg')

    assert _invoke(lexicon_dir, output_dir, 'pkg').exit_code == 0
    assert output_dir.joinpath('models', 'com', 'example', 'get_thing.py').is_file()

    lexicon_dir.joinpath('com.example.getThing.json').unlink()
    assert _invoke(lexicon_dir, output_dir, 'pkg').exit_code == 0

    assert not output_dir.joinpath('models', 'com').exists()
    assert 'ComExampleGetThing' not in output_dir.joinpath('models', '__init__.py').read_text()
    assert 'ComExampleGetThing' not in output_dir.joinpath('namespaces', 'sync_ns.py').read_text()


def test_no_ruff_cache_is_left_in_the_package(tmp_path: Path) -> None:
    output_dir = tmp_path.joinpath('pkg')

    assert _invoke(CUSTOM_LEXICON_DIR, output_dir, 'pkg').exit_code == 0

    assert not list(output_dir.rglob('.ruff_cache'))


def test_package_without_records_is_importable(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    _write_lexicon(lexicon_dir, _QUERY_LEXICON)
    package = 'no_records_pkg'
    output_dir = tmp_path.joinpath(package)

    assert _invoke(lexicon_dir, output_dir, package).exit_code == 0

    unknown_type = output_dir.joinpath('models', 'unknown_type.py').read_text()
    assert "UnknownRecordType: te.TypeAlias = 'base_unknown_type.UnknownRecordType'" in unknown_type

    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module(f'{package}.models.unknown_type')
        assert module.UnknownType is not None
    finally:
        sys.path.remove(str(tmp_path))
        for name in [n for n in sys.modules if n.startswith(package)]:
            del sys.modules[name]


def test_single_record_package_has_a_valid_union() -> None:
    from atproto_codegen.models.generator import _union_typehint

    assert _union_typehint([]) == 't.Any'
    assert _union_typehint(["'A'"]) == "'A'"
    assert _union_typehint(["'A'", "'B'"]) == "t.Union['A', 'B']"
