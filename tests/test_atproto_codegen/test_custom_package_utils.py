import typing as t

from atproto_client.models import utils


def test_utils_exports_resolve_through_the_fallback(custom_package: t.Any) -> None:
    """A generated package has no utils module of its own, so the helpers come from the SDK."""
    assert custom_package.get_or_create is utils.get_or_create
    assert custom_package.is_record_type is utils.is_record_type


def test_utils_exports_are_public(custom_package: t.Any) -> None:
    assert {'get_or_create', 'is_record_type', 'ids', 'XyzStatusphereStatus'} <= set(custom_package.__all__)
    assert all(hasattr(custom_package, name) for name in custom_package.__all__)
