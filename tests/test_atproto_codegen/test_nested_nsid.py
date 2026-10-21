import importlib
import json
import sys
import typing as t
from pathlib import Path

import pytest
from atproto_client import Client
from atproto_codegen.config import CodegenConfig
from atproto_codegen.models.generator import generate_models
from atproto_codegen.namespaces.generator import generate_namespaces

PACKAGE = 'nested_pkg'

#: the first NSID is also the namespace of the second one, like ``social.grain.gallery`` and its ``item``
_PARENT, _CHILD = 'xyz.nested.thing', 'xyz.nested.thing.part'


def _record_lexicon(nsid: str) -> t.Dict[str, object]:
    record = {'type': 'object', 'required': ['name'], 'properties': {'name': {'type': 'string'}}}
    return {'lexicon': 1, 'id': nsid, 'defs': {'main': {'type': 'record', 'key': 'tid', 'record': record}}}


@pytest.fixture(scope='module')
def package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[Path]:
    root = tmp_path_factory.mktemp('nested')
    lexicon_dir = root.joinpath('lexicons')
    lexicon_dir.mkdir()
    for nsid in (_PARENT, _CHILD):
        lexicon_dir.joinpath(f'{nsid}.json').write_text(json.dumps(_record_lexicon(nsid)))

    config = CodegenConfig(emit_lexicon_dirs=(lexicon_dir,), output_dir=root.joinpath(PACKAGE), package=PACKAGE)
    generate_models(config)
    generate_namespaces(config)

    sys.path.insert(0, str(root))
    yield root.joinpath(PACKAGE)


def test_parent_models_live_in_the_package_of_the_child(package: Path) -> None:
    thing_dir = package.joinpath('models', 'xyz', 'nested', 'thing')

    assert not thing_dir.with_suffix('.py').exists()
    assert 'class Record' in thing_dir.joinpath('__init__.py').read_text()


def test_models_of_both_lexicons_resolve(package: Path) -> None:
    models = importlib.import_module(f'{PACKAGE}.models')

    assert models.XyzNestedThing.Record(name='parent').py_type == _PARENT
    assert models.XyzNestedThingPart.Record(name='child').py_type == _CHILD


def test_namespace_serves_the_record_and_its_children(package: Path) -> None:
    sync_ns = importlib.import_module(f'{PACKAGE}.namespaces.sync_ns')
    namespace = sync_ns.XyzNestedNamespace(Client())

    assert isinstance(namespace.thing, sync_ns.XyzNestedThingRecord)
    assert isinstance(namespace.thing.part, sync_ns.XyzNestedThingPartRecord)


def test_sdk_gallery_record_and_item_are_reachable() -> None:
    from atproto_client import models

    client = Client()

    assert models.SocialGrainGallery.Record(created_at='2026-01-01T00:00:00.000Z', title='t').title == 't'
    assert callable(client.social.grain.gallery.get)
    assert callable(client.social.grain.gallery.item.get)
