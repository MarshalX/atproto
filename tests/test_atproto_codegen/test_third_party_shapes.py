import importlib
import json
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_client import Client
from atproto_client.models.utils import get_model_as_dict, get_or_create
from atproto_codegen.config import CodegenConfig
from atproto_codegen.exceptions import UnsupportedLexiconError
from atproto_codegen.models.generator import generate_models
from atproto_codegen.namespaces.generator import generate_namespaces
from pydantic import ValidationError

PACKAGE = 'shapes_pkg'

_INJECTED = 'INJECTED_BY_DESCRIPTION'
_HOSTILE_DESCRIPTION = f'First line.\nimport builtins; builtins.{_INJECTED} = True\n"""\\d and a quote"'


def _object(properties: t.Dict[str, t.Any], **overrides: t.Any) -> t.Dict[str, t.Any]:
    return {'type': 'object', 'properties': properties, **overrides}


def _lexicon(nsid: str, defs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    return {'lexicon': 1, 'id': nsid, 'defs': defs}


_LEXICONS = [
    _lexicon(
        'xyz.shapes.defs',
        {
            'tag': {'type': 'string', 'maxLength': 5, 'description': 'Free-form tag.'},
            'count': {'type': 'integer', 'minimum': 1},
            'raw': {'type': 'bytes'},
            'image': {'type': 'blob'},
            'kind': {'type': 'token'},
            'field': _object({'path': {'type': 'string'}}, required=['path']),
            'described': _object(
                {'value': {'type': 'string', 'description': _HOSTILE_DESCRIPTION}}, description=_HOSTILE_DESCRIPTION
            ),
            'holder': _object(
                {
                    'tag': {'type': 'ref', 'ref': '#tag'},
                    'count': {'type': 'ref', 'ref': '#count'},
                    'field': {'type': 'ref', 'ref': '#field'},
                    'limited': {'type': 'array', 'maxLength': 1, 'items': {'type': 'string'}},
                    'kind': {
                        'type': 'string',
                        'knownValues': ['#kind', '#missing', 'lex:xyz.shapes.defs#kind', "it's"],
                    },
                    'mode': {'type': 'string', 'const': 'fixed'},
                }
            ),
            'names': _object(
                {
                    'models': {'type': 'string'},
                    't': {'type': 'string'},
                    'from': {'type': 'string'},
                    'userDID': {'type': 'string'},
                    'time_us': {'type': 'integer'},
                    'small-arms': {'type': 'string'},
                    'ownerDID': {'type': 'ref', 'ref': '#tag'},
                    '$type': {'type': 'string'},
                },
                required=['userDID', 'ownerDID'],
            ),
            'nested': _object(
                {
                    'inner': _object({'deep': _object({'name': {'type': 'string'}}, required=['name'])}),
                    'items': {'type': 'array', 'items': _object({'id': {'type': 'integer'}}, required=['id'])},
                    'field': _object({'own': {'type': 'boolean'}}),
                },
                required=['inner'],
            ),
            'nestedField': _object({'taken': {'type': 'string'}}),
        },
    ),
    _lexicon(
        'xyz.4000.standard-reader.class',
        {
            'main': {
                'type': 'query',
                'description': _HOSTILE_DESCRIPTION,
                'output': {
                    'encoding': 'application/json',
                    'schema': _object({'result': _object({'ok': {'type': 'boolean'}})}),
                },
            }
        },
    ),
    _lexicon(
        'is.shapes.thing',
        {'main': {'type': 'record', 'key': 'tid', 'record': _object({'name': {'type': 'string'}}, required=['name'])}},
    ),
]


def _generate(root: Path, lexicons: t.List[t.Dict[str, t.Any]], package: str) -> None:
    lexicon_dir = root.joinpath('lexicons')
    lexicon_dir.mkdir()
    for lexicon in lexicons:
        lexicon_dir.joinpath(f'{lexicon["id"]}.json').write_text(json.dumps(lexicon), encoding='utf-8')

    config = CodegenConfig(emit_lexicon_dirs=(lexicon_dir,), output_dir=root.joinpath(package), package=package)
    generate_models(config)
    generate_namespaces(config)


@pytest.fixture(scope='module')
def package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[Path]:
    root = tmp_path_factory.mktemp('shapes')
    _generate(root, _LEXICONS, PACKAGE)

    sys.path.insert(0, str(root))
    yield root.joinpath(PACKAGE)


@pytest.fixture(scope='module')
def models(package: Path) -> t.Any:
    return importlib.import_module(f'{PACKAGE}.models')


@pytest.fixture(scope='module')
def defs(models: t.Any) -> t.Any:
    return models.XyzShapesDefs


def test_generated_code_compiles(package: Path) -> None:
    for path in package.rglob('*.py'):
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')


def test_descriptions_do_not_leave_comments_and_docstrings(package: Path, defs: t.Any) -> None:
    import builtins

    importlib.import_module(f'{PACKAGE}.namespaces.sync_ns')

    assert not hasattr(builtins, _INJECTED)
    assert '\\d and a quote"' in defs.Described.__doc__


def test_models_load_eagerly(models: t.Any) -> None:
    from atproto_client.models.models_loader import load_models

    load_models(f'{PACKAGE}.models')

    assert models.XyzShapesDefs.Nested.__pydantic_complete__


def test_unsafe_nsid_segments_get_safe_module_names(package: Path, models: t.Any) -> None:
    assert package.joinpath('models', 'xyz', '_4000', 'standard_reader', 'class_.py').is_file()
    assert package.joinpath('models', 'is_', 'shapes', 'thing.py').is_file()

    assert models.ids.Xyz4000StandardReaderClass == 'xyz.4000.standard-reader.class'
    assert models.IsShapesThing.Record(name='n').py_type == 'is.shapes.thing'


def test_unsafe_nsid_segments_get_safe_namespace_attributes(package: Path) -> None:
    sync_ns = importlib.import_module(f'{PACKAGE}.namespaces.sync_ns')
    client_module = importlib.import_module(f'{PACKAGE}.client')

    assert callable(sync_ns.XyzNamespace(Client())._4000.standard_reader.class_)
    assert isinstance(client_module.ShapesPkgClient().is_.shapes.thing, sync_ns.IsShapesThingRecord)


def test_primitive_defs_are_usable_as_references(defs: t.Any) -> None:
    holder = get_or_create({'tag': 'short', 'count': 2}, defs.Holder)

    assert (holder.tag, holder.count) == ('short', 2)
    with pytest.raises(Exception, match='at most 5 characters'):
        get_or_create({'tag': 'too long'}, defs.Holder)
    with pytest.raises(Exception, match='greater than or equal to 1'):
        get_or_create({'count': 0}, defs.Holder)


def test_definition_named_like_an_import_does_not_shadow_it(defs: t.Any) -> None:
    holder = get_or_create({'field': {'path': 'p'}, 'limited': ['one']}, defs.Holder)

    assert isinstance(holder.field, defs.Field_)
    with pytest.raises(Exception, match='at most 1 item'):
        get_or_create({'limited': ['one', 'two']}, defs.Holder)


def test_known_values_that_are_not_tokens_stay_strings(defs: t.Any) -> None:
    for value in ('xyz.shapes.defs#kind', '#missing', 'lex:xyz.shapes.defs#kind', "it's", 'anything'):
        assert defs.Holder(kind=value).kind == value


def test_string_const_is_a_literal(defs: t.Any) -> None:
    assert defs.Holder(mode='fixed').mode == 'fixed'
    with pytest.raises(ValidationError):
        defs.Holder(mode='other')


def test_property_names_round_trip(defs: t.Any) -> None:
    data = {
        'models': 'm',
        't': 't',
        'from': 'f',
        'userDID': 'did:plc:user',
        'time_us': 1,
        'small-arms': 's',
        'ownerDID': 'tag',
    }
    names = get_or_create(data, defs.Names)

    assert (names.models_, names.t_, names.from_) == ('m', 't', 'f')
    assert (names.user_did, names.time_us, names.small_arms, names.owner_did) == ('did:plc:user', 1, 's', 'tag')
    assert get_model_as_dict(names) == {**data, '$type': 'xyz.shapes.defs#names'}
    assert defs.Names(user_did='did:plc:user', owner_did='tag').user_did == 'did:plc:user'


def test_inline_objects_become_models(defs: t.Any, models: t.Any) -> None:
    data = {'inner': {'deep': {'name': 'n'}}, 'items': [{'id': 1}], 'field': {'own': True}}
    nested = get_or_create(data, defs.Nested)

    assert isinstance(nested.inner, defs.NestedInner)
    assert isinstance(nested.inner.deep, defs.NestedInnerDeep)
    assert isinstance(nested.items[0], defs.NestedItemsItem)
    assert nested.inner.deep.name == 'n'
    # the name `NestedField` belongs to a definition of the lexicon
    assert isinstance(nested.field, defs.NestedFieldObject)
    assert get_model_as_dict(nested) == {**data, '$type': 'xyz.shapes.defs#nested'}

    response = models.Xyz4000StandardReaderClass.Response(result={'ok': True})
    assert isinstance(response.result, models.Xyz4000StandardReaderClass.ResponseResult)


def test_union_body_is_reported_as_unsupported(tmp_path: Path) -> None:
    lexicon = _lexicon(
        'xyz.shapes.resolve',
        {
            'main': {
                'type': 'query',
                'output': {'encoding': 'application/json', 'schema': {'type': 'union', 'refs': ['#a']}},
            },
            'a': _object({}),
        },
    )

    with pytest.raises(UnsupportedLexiconError, match=r'xyz\.shapes\.resolve'):
        _generate(tmp_path, [lexicon], 'union_pkg')


def test_definition_named_like_a_module_class_keeps_its_own(tmp_path: Path) -> None:
    record = {'type': 'record', 'key': 'tid', 'record': _object({'inner': {'type': 'ref', 'ref': '#record'}})}
    lexicons = [
        _lexicon('xyz.clash.thing', {'main': record, 'record': _object({'value': {'type': 'string'}})}),
        _lexicon(
            'xyz.clash.getThing',
            {
                'main': {
                    'type': 'query',
                    'output': {
                        'encoding': 'application/json',
                        'schema': _object({'r': {'type': 'ref', 'ref': '#response'}}),
                    },
                },
                'response': _object({'ok': {'type': 'boolean'}}),
                # not a class of a query module, so the name is free
                'record': _object({'free': {'type': 'string'}}),
            },
        ),
        _lexicon('xyz.clash.user', {'main': _object({'inner': {'type': 'ref', 'ref': 'xyz.clash.thing#record'}})}),
    ]
    package = 'clash_names_pkg'
    _generate(tmp_path, lexicons, package)
    sys.path.insert(0, str(tmp_path))
    models = importlib.import_module(f'{package}.models')

    thing = get_or_create({'inner': {'value': 'v'}}, models.XyzClashThing.Record)
    assert isinstance(thing.inner, models.XyzClashThing.RecordDef)
    assert thing.inner.py_type == 'xyz.clash.thing#record'

    response = get_or_create({'r': {'ok': True}}, models.XyzClashGetThing.Response)
    assert isinstance(response.r, models.XyzClashGetThing.ResponseDef)
    assert models.XyzClashGetThing.Record(free='f').py_type == 'xyz.clash.getThing#record'

    user = get_or_create({'inner': {'value': 'v'}}, models.XyzClashUser.Main)
    assert isinstance(user.inner, models.XyzClashThing.RecordDef)


_SHARED_ROOT_LEXICONS = [
    _lexicon(
        'app.shapes.thing',
        {'main': {'type': 'record', 'key': 'tid', 'record': _object({'name': {'type': 'string'}})}},
    ),
    _lexicon('com.atproto.repo.shapesExtra', {'main': {'type': 'query'}}),
]


def test_namespaces_extend_the_ones_of_the_sdk(tmp_path: Path) -> None:
    package = 'shared_root_pkg'
    _generate(tmp_path, _SHARED_ROOT_LEXICONS, package)
    sys.path.insert(0, str(tmp_path))

    client = importlib.import_module(f'{package}.client').SharedRootPkgClient()
    async_client = importlib.import_module(f'{package}.async_client').AsyncSharedRootPkgClient()

    for attached in (client, async_client):
        assert callable(attached.app.shapes.thing.create)
        assert callable(attached.app.bsky.feed.post.create)
        assert callable(attached.com.atproto.repo.shapes_extra)
        assert callable(attached.com.atproto.repo.create_record)
        assert callable(attached.com.atproto.server.describe_server)

    plain: t.Any = Client()
    importlib.import_module(f'{package}.client').attach_namespaces(plain)
    assert callable(plain.app.bsky.feed.post.create)
    assert callable(plain.app.shapes.thing.create)
