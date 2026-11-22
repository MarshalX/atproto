import importlib
import json
import shutil
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_cli import atproto_cli
from atproto_client import Client
from atproto_client.exceptions import ModelError
from atproto_client.models import string_formats
from atproto_client.models.utils import get_or_create
from click.testing import CliRunner

# Ref: https://github.com/bluesky-social/atproto/tree/b5fd12fa57b10cf068efa879812f558780f37109/packages/lex/lex/lexicons/com/example
SPACE_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'space_lexicons').absolute()
PACKAGE = 'space_type_pkg'

_SPACE = 'at://did:plc:asdf123/space/com.example.space/default'
_SPACE_RECORD = f'{_SPACE}/did:plc:user1/com.example.spaceRecord/abc123'

_SPACE_REF = {'type': 'string', 'format': 'space-ref'}

_LEXICONS = [
    {
        'lexicon': 1,
        'id': 'com.example.forum',
        'defs': {'main': {'type': 'space', 'key': 'any', 'collections': ['com.example.spaceRecord']}},
    },
    {
        'lexicon': 1,
        'id': 'com.example.getSpace',
        'defs': {
            'main': {
                'type': 'query',
                'parameters': {'type': 'params', 'required': ['space'], 'properties': {'space': _SPACE_REF}},
                'output': {
                    'encoding': 'application/json',
                    'schema': {
                        'type': 'object',
                        'required': ['space'],
                        'properties': {'space': _SPACE_REF, 'related': {'type': 'array', 'items': _SPACE_REF}},
                    },
                },
            }
        },
    },
]


@pytest.fixture(scope='module')
def package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[Path]:
    root = tmp_path_factory.mktemp('space_type')
    lexicon_dir = root.joinpath('lexicons')
    shutil.copytree(SPACE_LEXICON_DIR, lexicon_dir)
    for lexicon in _LEXICONS:
        lexicon_dir.joinpath(f'{lexicon["id"]}.json').write_text(json.dumps(lexicon), encoding='utf-8')

    output_dir = str(root.joinpath(PACKAGE))
    args = ['gen', '--lexicon-dir', str(lexicon_dir), 'custom', '--output-dir', output_dir, '--package', PACKAGE]
    result = CliRunner().invoke(atproto_cli, args)
    assert result.exit_code == 0, result.output

    sys.path.insert(0, str(root))
    yield root.joinpath(PACKAGE)


@pytest.fixture(scope='module')
def models(package: Path) -> t.Any:
    return importlib.import_module(f'{PACKAGE}.models')


def test_space_ref_fields_are_typed(models: t.Any) -> None:
    params = models.ComExampleGetSpace.Params
    response = models.ComExampleGetSpace.Response

    assert params.model_fields['space'].annotation is string_formats.SpaceRef
    assert response.model_fields['space'].annotation is string_formats.SpaceRef
    assert response.model_fields['related'].annotation == t.Optional[t.List[string_formats.SpaceRef]]


def test_space_ref_fields_are_validated_in_strict_mode(models: t.Any) -> None:
    params = models.ComExampleGetSpace.Params

    assert get_or_create({'space': _SPACE}, params, strict_string_format=True).space == _SPACE
    assert get_or_create({'space': _SPACE_RECORD}, params).space == _SPACE_RECORD
    with pytest.raises(ModelError, match='Invalid space reference'):
        get_or_create({'space': _SPACE_RECORD}, params, strict_string_format=True)


def test_space_type_has_no_module(package: Path, models: t.Any) -> None:
    assert not package.joinpath('models', 'com', 'example', 'forum.py').exists()
    assert 'ComExampleForum' not in dir(models)
    assert not hasattr(models.ids, 'ComExampleForum')


def test_definitions_beside_space_type_are_generated(models: t.Any) -> None:
    record = get_or_create({'meta': {'text': 'hello'}}, models.ComExampleSpaceRecord.Record)

    assert isinstance(record.meta, models.ComExampleSpace.Meta)
    assert record.meta.text == 'hello'
    assert models.ids.ComExampleSpace == 'com.example.space'
    assert not hasattr(models.ComExampleSpace, 'Main')


def test_space_type_has_no_namespace_member(package: Path) -> None:
    sync_ns = importlib.import_module(f'{PACKAGE}.namespaces.sync_ns')
    namespace = sync_ns.ComExampleNamespace(Client())

    assert callable(namespace.get_space)
    assert not hasattr(namespace, 'space')
    assert not hasattr(namespace, 'forum')
