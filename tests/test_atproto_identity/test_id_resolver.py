from atproto_identity.did.resolver import DidResolver
from atproto_identity.handle.resolver import HandleResolver
from atproto_identity.resolver import IdResolver


def test_id_resolver_did_resolver() -> None:
    did_resolver = IdResolver().did
    assert isinstance(did_resolver, DidResolver)


def test_id_resolver_handle_resolver() -> None:
    handle_resolver = IdResolver().handle
    assert isinstance(handle_resolver, HandleResolver)
