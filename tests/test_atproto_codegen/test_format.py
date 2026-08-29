import subprocess
import sys
from pathlib import Path

import pytest
from atproto_codegen import utils
from atproto_codegen.config import DEFAULT_LEXICON_DIR, CodegenConfig
from atproto_codegen.models.generator import generate_models
from atproto_codegen.namespaces.generator import generate_namespaces
from atproto_codegen.utils import RUFF_CONFIG_PATH, RuffNotFoundError, find_ruff

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()


@pytest.fixture
def generated_package(tmp_path: Path) -> Path:
    root = tmp_path.joinpath('mypkg')
    config = CodegenConfig(
        emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,),
        ref_lexicon_dirs=(DEFAULT_LEXICON_DIR,),
        output_dir=root,
        package='mypkg',
    )
    generate_models(config)
    generate_namespaces(config)

    return root


def _ruff(*args: str, cwd: Path) -> 'subprocess.CompletedProcess[str]':
    return subprocess.run(  # noqa: S603
        [find_ruff(), *args, f'--config={RUFF_CONFIG_PATH}', '.'],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_config_ships_with_the_package() -> None:
    assert RUFF_CONFIG_PATH.is_file()


def test_find_ruff_locates_the_binary() -> None:
    assert Path(find_ruff()).is_file()


def test_missing_ruff_raises_with_install_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    find_ruff.cache_clear()
    monkeypatch.setattr(utils.sysconfig, 'get_path', lambda *a, **kw: None)
    monkeypatch.setattr(utils.shutil, 'which', lambda _: None)

    with pytest.raises(RuffNotFoundError, match='pip install ruff'):
        find_ruff()

    find_ruff.cache_clear()


def test_generated_package_passes_lint(generated_package: Path) -> None:
    result = _ruff('check', cwd=generated_package)

    assert result.returncode == 0, result.stdout


def test_generated_package_is_formatted(generated_package: Path) -> None:
    result = _ruff('format', '--check', cwd=generated_package)

    assert result.returncode == 0, result.stdout


def test_generated_package_has_importable_roots(generated_package: Path) -> None:
    assert generated_package.joinpath('__init__.py').is_file()
    assert generated_package.joinpath('models', '__init__.py').is_file()
    assert generated_package.joinpath('namespaces', '__init__.py').is_file()


@pytest.mark.skipif(sys.platform == 'win32', reason='quoting differs on Windows')
def test_style_ignores_the_surrounding_project(generated_package: Path, tmp_path: Path) -> None:
    """A hostile Ruff config next to the output does not change how generated code is formatted."""
    tmp_path.joinpath('pyproject.toml').write_text(
        '[tool.ruff]\nline-length = 50\n\n[tool.ruff.format]\nquote-style = "double"\n'
    )
    status = generated_package.joinpath('models', 'xyz', 'statusphere', 'status.py').read_text()

    assert "'" in status
    assert any(len(line) > 50 for line in status.splitlines())
