import importlib
import json
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_cli import atproto_cli
from atproto_client.models.dot_dict import DotDict
from atproto_client.models.utils import get_or_create
from atproto_lexicon.exceptions import LexiconParsingError
from click.testing import CliRunner

PACKAGE = 'skip_invalid_pkg'


def _object(properties: t.Dict[str, t.Any], **overrides: t.Any) -> t.Dict[str, t.Any]:
    return {'type': 'object', 'properties': properties, **overrides}


def _lexicon(nsid: str, defs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {'lexicon': 1, 'id': nsid, 'defs': defs}


def _query(schema: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {'type': 'query', 'output': {'encoding': 'application/json', 'schema': schema}}


def _ref(ref: str) -> t.Dict[str, t.Any]:
    return {'type': 'ref', 'ref': ref}


_UNPARSEABLE = _lexicon('xyz.skipping.broken', {'main': {'type': 'space'}})

_LEXICONS = [
    _UNPARSEABLE,
    _lexicon(
        'xyz.skipping.defs',
        {
            'known': _object({'name': {'type': 'string'}}),
            'holder': _object(
                {
                    'unpublished': _ref('xyz.missing.thing'),
                    'skipped': _ref('xyz.skipping.broken'),
                    'missingDef': _ref('#nope'),
                    'malformed': _ref('not a reference'),
                    'list': {'type': 'array', 'items': _ref('xyz.missing.thing')},
                    'open': {'type': 'union', 'refs': ['#known', '#nope']},
                    'closed': {'type': 'union', 'closed': True, 'refs': ['#known', '#nope']},
                    'allMissing': {'type': 'union', 'closed': True, 'refs': ['#nope']},
                    'known': _ref('#known'),
                }
            ),
        },
    ),
    _lexicon('xyz.skipping.getKnown', {'main': _query(_ref('xyz.skipping.defs#known'))}),
    _lexicon('xyz.skipping.getMissing', {'main': _query(_ref('xyz.missing.thing'))}),
    _lexicon('xyz.skipping.getUnion', {'main': _query({'type': 'union', 'refs': ['xyz.skipping.defs#known']})}),
    _lexicon(
        'xyz.skipping.subscribe',
        {
            'main': {'type': 'subscription', 'message': {'schema': {'type': 'union', 'refs': ['#event', '#nope']}}},
            'event': _object({'seq': {'type': 'integer'}}),
        },
    ),
    # both collapse to the same plain alias
    _lexicon('xyz.skipping.audioSettings', {'main': _object({'flat': {'type': 'string'}})}),
    _lexicon('xyz.skipping.audio.settings', {'main': _object({'nested': {'type': 'string'}})}),
]


def _write_lexicons(root: Path, lexicons: t.List[t.Dict[str, t.Any]]) -> Path:
    lexicon_dir = root.joinpath('lexicons')
    lexicon_dir.mkdir()
    for lexicon in lexicons:
        lexicon_dir.joinpath(f'{lexicon["id"]}.json').write_text(json.dumps(lexicon), encoding='utf-8')

    return lexicon_dir


def _run_cli(root: Path, lexicon_dir: Path, package: str, *extra: str) -> t.Any:
    output_dir = str(root.joinpath(package))
    args = ['gen', '--lexicon-dir', str(lexicon_dir), 'custom', '--output-dir', output_dir, '--package', package]
    return CliRunner().invoke(atproto_cli, [*args, *extra])


@pytest.fixture(scope='module')
def output(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[str]:
    root = tmp_path_factory.mktemp('skip_invalid')
    result = _run_cli(root, _write_lexicons(root, _LEXICONS), PACKAGE, '--skip-invalid')
    assert result.exit_code == 0, result.output

    sys.path.insert(0, str(root))
    yield result.output


@pytest.fixture(scope='module')
def models(output: str) -> t.Any:
    from atproto_client.models.models_loader import load_models

    load_models(f'{PACKAGE}.models')
    return importlib.import_module(f'{PACKAGE}.models')


def test_strict_run_fails_on_the_unparseable_lexicon(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, _write_lexicons(tmp_path, _LEXICONS), 'strict_pkg')

    assert isinstance(result.exception, LexiconParsingError)


def test_strict_run_fails_on_an_unresolved_reference(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, _write_lexicons(tmp_path, _LEXICONS[1:]), 'strict_refs_pkg')

    assert result.exit_code != 0
    assert 'xyz.skipping.defs#nope' in result.output


def test_everything_left_out_is_reported(output: str) -> None:
    for expected in (
        'Skipped xyz.skipping.broken.json',
        "Unresolved reference 'xyz.missing.thing' in xyz.skipping.defs",
        "Unresolved reference 'xyz.skipping.broken' in xyz.skipping.defs",
        "Unresolved reference '#nope' in xyz.skipping.defs",
        "Unresolved reference 'not a reference' in xyz.skipping.defs",
        'Skipped method xyz.skipping.getMissing',
        'Skipped method xyz.skipping.getUnion',
    ):
        assert expected in output


def test_unresolved_references_become_unknown(models: t.Any) -> None:
    defs = models.XyzSkippingDefs
    data = {
        'unpublished': {'a': 1},
        'skipped': {'b': 2},
        'missingDef': {'c': 3},
        'malformed': {'d': 4},
        'list': [{'e': 5}],
        'known': {'name': 'n'},
    }
    holder = get_or_create(data, defs.Holder)

    assert isinstance(holder.unpublished, DotDict)
    assert holder.unpublished.a == 1
    assert (holder.skipped.b, holder.missing_def.c, holder.malformed.d, holder.list[0].e) == (2, 3, 4, 5)
    assert isinstance(holder.known, defs.Known)


def test_unions_keep_their_resolved_members(models: t.Any) -> None:
    defs = models.XyzSkippingDefs
    known = {'$type': 'xyz.skipping.defs#known', 'name': 'n'}
    other = {'$type': 'xyz.skipping.defs#nope', 'value': 1}

    holder = get_or_create({'open': known, 'closed': other, 'allMissing': other}, defs.Holder)

    assert isinstance(holder.open, defs.Known)
    # a closed union that lost a member accepts what it can no longer name
    assert holder.closed.value == 1
    assert holder.all_missing.py_type == 'xyz.skipping.defs#nope'
    assert isinstance(get_or_create({'closed': known}, defs.Holder).closed, defs.Known)


def test_methods_without_a_usable_body_are_skipped(models: t.Any) -> None:
    sync_ns = importlib.import_module(f'{PACKAGE}.namespaces.sync_ns')
    namespace = sync_ns.XyzSkippingNamespace

    assert hasattr(namespace, 'get_known')
    assert not hasattr(namespace, 'get_missing')
    assert not hasattr(namespace, 'get_union')


def test_subscription_keeps_its_resolved_messages(models: t.Any) -> None:
    subscriptions = importlib.import_module(f'{PACKAGE}.subscriptions')

    assert list(subscriptions.XYZ_SKIPPING_SUBSCRIBE_MESSAGE_TYPE_TO_MODEL) == ['#event']


def test_colliding_aliases_are_told_apart(models: t.Any) -> None:
    assert models.ids.XyzSkippingAudioSettings == 'xyz.skipping.audioSettings'
    assert models.ids.Xyz_Skipping_Audio_Settings == 'xyz.skipping.audio.settings'
    assert models.XyzSkippingAudioSettings.Main(flat='f').flat == 'f'
    assert models.Xyz_Skipping_Audio_Settings.Main(nested='n').nested == 'n'


def test_nothing_to_generate_is_an_error(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, _write_lexicons(tmp_path, [_UNPARSEABLE]), 'empty_pkg', '--skip-invalid')

    assert result.exit_code != 0
    assert 'None of the .json lexicons could be parsed' in result.output
