import sys
import typing as t
from pathlib import Path

import pytest
from atproto_codegen.config import DEFAULT_LEXICON_DIR, CodegenConfig
from atproto_codegen.models.generator import generate_models

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()
PACKAGE = 'chained_pkg'


@pytest.fixture(scope='module')
def custom_package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[t.Any]:
    """Generate a package from the custom lexicons and import it."""
    root = tmp_path_factory.mktemp('chained')
    generate_models(
        CodegenConfig(
            emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,),
            ref_lexicon_dirs=(DEFAULT_LEXICON_DIR,),
            output_dir=root.joinpath(PACKAGE),
            package=PACKAGE,
        )
    )

    sys.path.insert(0, str(root))
    try:
        import importlib

        yield importlib.import_module(f'{PACKAGE}.models')
    finally:
        sys.path.remove(str(root))
        for name in [n for n in sys.modules if n.startswith(PACKAGE)]:
            del sys.modules[name]


def test_generated_package_is_importable(custom_package: t.Any) -> None:
    assert custom_package.__name__ == f'{PACKAGE}.models'


def test_own_lexicons_resolve_locally(custom_package: t.Any) -> None:
    assert custom_package.XyzStatusphereStatus.Record.__module__.startswith(PACKAGE)


def test_sdk_lexicons_resolve_through_the_fallback(custom_package: t.Any) -> None:
    """A name the generated package does not define comes from the SDK."""
    strong_ref = custom_package.ComAtprotoRepoStrongRef

    assert strong_ref.Main.__module__.startswith('atproto_client')


def test_unknown_names_still_raise(custom_package: t.Any) -> None:
    with pytest.raises(AttributeError):
        custom_package.ThisLexiconDoesNotExist  # noqa: B018


def test_dir_includes_both_packages(custom_package: t.Any) -> None:
    names = dir(custom_package)

    assert 'XyzStatusphereStatus' in names
    assert 'AppBskyFeedPost' in names


def test_model_with_cross_package_reference_validates(custom_package: t.Any) -> None:
    """The whole point: a custom record whose field type lives in the SDK."""
    record = custom_package.XyzStatusphereStatus.Record(
        status='👍',
        created_at='2026-08-29T00:00:00.000Z',
        subject={'uri': 'at://did:plc:test/app.bsky.feed.post/abc', 'cid': 'bafyreiabc123'},
    )

    assert record.subject.uri == 'at://did:plc:test/app.bsky.feed.post/abc'
    assert type(record.subject).__module__.startswith('atproto_client')


def test_record_round_trips_through_json(custom_package: t.Any) -> None:
    from atproto_client.models.utils import get_model_as_dict

    record = custom_package.XyzStatusphereStatus.Record(status='🎉', created_at='2026-08-29T00:00:00.000Z')
    as_dict = get_model_as_dict(record)

    assert as_dict['$type'] == 'xyz.statusphere.status'
    assert as_dict['status'] == '🎉'
