import json
import typing as t
from pathlib import Path

import pytest
from atproto_codegen.config import CodegenConfig
from atproto_codegen.exceptions import UnresolvedReferenceError
from atproto_codegen.models.generator import generate_models


def _write_lexicon(lexicon_dir: Path, nsid: str, properties: t.Dict[str, t.Any]) -> None:
    lexicon = {'lexicon': 1, 'id': nsid, 'defs': {'main': {'type': 'object', 'properties': properties}}}
    lexicon_dir.mkdir(parents=True, exist_ok=True)
    lexicon_dir.joinpath(f'{nsid}.json').write_text(json.dumps(lexicon))


def test_every_missing_lexicon_is_reported_before_anything_is_written(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    _write_lexicon(
        lexicon_dir,
        'com.example.thing',
        {
            'first': {'type': 'ref', 'ref': 'com.missing.first#view'},
            'second': {'type': 'union', 'refs': ['com.missing.second']},
        },
    )
    output_dir = tmp_path.joinpath('pkg')

    with pytest.raises(UnresolvedReferenceError) as exc_info:
        generate_models(CodegenConfig(emit_lexicon_dirs=(lexicon_dir,), output_dir=output_dir))

    assert "'com.missing.first' referenced by com.example.thing" in str(exc_info.value)
    assert "'com.missing.second' referenced by com.example.thing" in str(exc_info.value)
    assert not output_dir.exists()


def test_custom_package_leaves_foreign_refs_to_the_base_package(tmp_path: Path) -> None:
    lexicon_dir = tmp_path.joinpath('lexicons')
    _write_lexicon(lexicon_dir, 'com.example.defs', {})
    _write_lexicon(
        lexicon_dir,
        'com.example.thing',
        {
            'foreign': {'type': 'ref', 'ref': 'com.atproto.repo.strongRef'},
            'local': {'type': 'ref', 'ref': 'com.example.defs#nope'},
        },
    )
    output_dir = tmp_path.joinpath('pkg')
    config = CodegenConfig(emit_lexicon_dirs=(lexicon_dir,), output_dir=output_dir, package='pkg')

    with pytest.raises(UnresolvedReferenceError) as exc_info:
        generate_models(config)

    assert "'com.example.defs#nope'" in str(exc_info.value)
    assert 'com.atproto.repo.strongRef' not in str(exc_info.value)
    assert not output_dir.exists()
