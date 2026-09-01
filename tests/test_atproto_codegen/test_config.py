from pathlib import Path

import pytest
from atproto_codegen.config import CodegenConfig, get_config, use_config
from atproto_codegen.models import builder
from atproto_codegen.models.generator import generate_models
from atproto_core.nsid import NSID

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()

UNUSED_OUTPUT_DIR = Path(__file__).parent.joinpath('__never_written__')


def _custom_config(output_dir: Path, package: str = 'custom_pkg') -> CodegenConfig:
    return CodegenConfig(emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,), output_dir=output_dir, package=package)


@pytest.fixture
def generated(tmp_path: Path) -> Path:
    generate_models(_custom_config(tmp_path))
    return tmp_path.joinpath('models')


def test_default_config_targets_the_sdk() -> None:
    config = get_config()

    assert config.is_self_gen
    assert config.models_package == 'atproto_client.models'
    assert config.models_output_dir.name == 'models'


def test_use_config_restores_the_previous_config() -> None:
    custom = _custom_config(UNUSED_OUTPUT_DIR)

    with use_config(custom):
        assert get_config() is custom

    assert get_config().is_self_gen


def test_reference_records_come_from_the_base_package() -> None:
    """A record is resolvable when it is emitted or when the package the models fall back to defines it."""
    config = _custom_config(UNUSED_OUTPUT_DIR)

    assert builder.is_record(NSID.from_str('xyz.statusphere.status'), config)
    assert builder.is_record(NSID.from_str('app.bsky.feed.post'), config)
    assert not builder.is_record(NSID.from_str('app.bsky.actor.defs'), config)
    assert not builder.is_record(NSID.from_str('xyz.statusphere.getStatuses'), config)


def test_reference_records_are_never_read_from_the_lexicons() -> None:
    config = _custom_config(UNUSED_OUTPUT_DIR)

    assert {str(nsid) for nsid in builder.build_record_models(config)} == {'xyz.statusphere.status'}
    assert 'app.bsky.feed.post' in builder.reference_record_types(config)


def test_self_generation_has_no_reference_records() -> None:
    """The SDK emits every lexicon it knows, so there is nothing to fall back to."""
    assert builder.reference_record_types(CodegenConfig()) == frozenset()


def test_lexicon_databases_are_isolated_per_config() -> None:
    custom = _custom_config(UNUSED_OUTPUT_DIR)

    assert len(builder.build_record_models(custom)) == 1
    assert len(builder.build_record_models(CodegenConfig())) > 1


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

    assert "'xyz.statusphere.status': 'XyzStatusphereStatus'" in type_conversion
    assert 'app.bsky' not in type_conversion


def test_ids_registry_maps_aliases_to_nsids(generated: Path) -> None:
    init = generated.joinpath('__init__.py').read_text()

    assert "XyzStatusphereGetStatuses: str = 'xyz.statusphere.getStatuses'" in init
    assert "XyzStatusphereStatus: str = 'xyz.statusphere.status'" in init
