import typing as t

import pytest

from .conftest import PACKAGE


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


def test_custom_record_resolves_from_type(custom_package: t.Any) -> None:
    """A record type a generated package owns decodes to its model, not to a DotDict."""
    from atproto_client.models.utils import get_or_create

    decoded = get_or_create(
        {'$type': 'xyz.statusphere.status', 'status': '🚀', 'createdAt': '2026-08-29T00:00:00.000Z'},
        None,
        strict=False,
    )

    assert type(decoded) is custom_package.XyzStatusphereStatus.Record
    assert decoded.status == '🚀'


def test_unregistered_type_resolves_to_nothing() -> None:
    """An unregistered ``$type`` is not resolvable, exactly as before the registry."""
    from atproto_client.models.utils import get_or_create

    assert get_or_create({'$type': 'zzz.nobody.owns.this', 'a': 1}, None, strict=False) is None


def test_registration_does_not_eagerly_import_models(custom_package: t.Any) -> None:
    """Registration holds names, so no model module is imported until a record is decoded."""
    import importlib
    import sys

    module = f'{PACKAGE}.models.type_conversion'
    sys.modules.pop(f'{PACKAGE}.models.xyz.statusphere.status', None)
    importlib.reload(importlib.import_module(module))

    assert f'{PACKAGE}.models.xyz.statusphere.status' not in sys.modules
