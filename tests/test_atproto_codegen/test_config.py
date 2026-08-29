from pathlib import Path

import pytest
from atproto_codegen.config import DEFAULT_LEXICON_DIR, CodegenConfig, get_config, use_config
from atproto_codegen.models import builder
from atproto_codegen.models.builder import Scope
from atproto_codegen.models.generator import generate_models

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()

UNUSED_OUTPUT_DIR = Path(__file__).parent.joinpath('__never_written__')


def _custom_config(output_dir: Path, *, with_refs: bool, package: str = 'custom_pkg') -> CodegenConfig:
    return CodegenConfig(
        emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,),
        ref_lexicon_dirs=(DEFAULT_LEXICON_DIR,) if with_refs else (),
        output_dir=output_dir,
        package=package,
    )


@pytest.fixture
def generated(tmp_path: Path) -> Path:
    generate_models(_custom_config(tmp_path, with_refs=True))
    return tmp_path.joinpath('models')


def test_default_config_targets_the_sdk() -> None:
    config = get_config()

    assert config.is_self_gen
    assert config.models_package == 'atproto_client.models'
    assert config.models_output_dir.name == 'models'


def test_use_config_restores_the_previous_config() -> None:
    custom = _custom_config(UNUSED_OUTPUT_DIR, with_refs=False)

    with use_config(custom):
        assert get_config() is custom

    assert get_config().is_self_gen


def test_emit_scope_excludes_reference_lexicons() -> None:
    config = _custom_config(UNUSED_OUTPUT_DIR, with_refs=True)

    emitted = builder.build_record_models(config, Scope.EMIT)
    resolvable = builder.build_record_models(config, Scope.ALL)

    assert {str(nsid) for nsid in emitted} == {'xyz.statusphere.status'}
    assert 'app.bsky.feed.post' in {str(nsid) for nsid in resolvable}


def test_lexicon_databases_are_isolated_per_config() -> None:
    with_refs = _custom_config(UNUSED_OUTPUT_DIR, with_refs=True)
    without_refs = _custom_config(UNUSED_OUTPUT_DIR, with_refs=False)

    assert len(builder.build_record_models(with_refs, Scope.ALL)) > 1
    assert len(builder.build_record_models(without_refs, Scope.ALL)) == 1


def test_only_emitted_lexicons_produce_modules(generated: Path) -> None:
    assert generated.joinpath('xyz', 'statusphere', 'status.py').exists()
    assert not generated.joinpath('app').exists()
    assert not generated.joinpath('com').exists()


def test_reference_to_sdk_record_resolves_to_record_not_main(generated: Path) -> None:
    """A ``#main`` reference into a lexicon that is resolved against but not emitted names ``Record``."""
    status = generated.joinpath('xyz', 'statusphere', 'status.py').read_text()

    assert "'models.AppBskyFeedPost.Record'" in status
    assert 'AppBskyFeedPost.Main' not in status


def test_reference_to_sdk_definition_resolves(generated: Path) -> None:
    status = generated.joinpath('xyz', 'statusphere', 'status.py').read_text()

    assert "'models.ComAtprotoRepoStrongRef.Main'" in status
    assert "'models.AppBskyActorDefs.ProfileViewBasic'" in status


def test_local_references_resolve_within_the_generated_package(generated: Path) -> None:
    get_statuses = generated.joinpath('xyz', 'statusphere', 'get_statuses.py').read_text()

    assert "'models.XyzStatusphereStatus.StatusView'" in get_statuses


def test_generated_imports_point_at_the_custom_package(generated: Path) -> None:
    status = generated.joinpath('xyz', 'statusphere', 'status.py').read_text()
    init = generated.joinpath('__init__.py').read_text()

    assert 'from custom_pkg import models' in status
    # base classes still come from the SDK
    assert 'from atproto_client.models import base' in status
    assert 'from custom_pkg.models.xyz.statusphere import status as XyzStatusphereStatus' in init


def test_record_type_database_covers_only_emitted_records(generated: Path) -> None:
    type_conversion = generated.joinpath('type_conversion.py').read_text()

    assert "'xyz.statusphere.status': models.XyzStatusphereStatus.Record" in type_conversion
    assert 'app.bsky' not in type_conversion


def test_ids_registry_maps_aliases_to_nsids(generated: Path) -> None:
    init = generated.joinpath('__init__.py').read_text()

    assert "XyzStatusphereGetStatuses: str = 'xyz.statusphere.getStatuses'" in init
    assert "XyzStatusphereStatus: str = 'xyz.statusphere.status'" in init
