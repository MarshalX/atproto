from atproto_identity.did.resolver import AsyncDidResolver
from atproto_identity.handle.resolver import AsyncHandleResolver
from atproto_identity.resolver import AsyncIdResolver


def test_id_resolver_did_resolver() -> None:
    did_resolver = AsyncIdResolver().did
    assert isinstance(did_resolver, AsyncDidResolver)


def test_id_resolver_handle_resolver() -> None:
    handle_resolver = AsyncIdResolver().handle
    assert isinstance(handle_resolver, AsyncHandleResolver)
