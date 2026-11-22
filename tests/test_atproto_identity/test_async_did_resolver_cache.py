import pytest
from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
from atproto_identity.did.resolver import AsyncDidResolver
from atproto_identity.exceptions import DidNotFoundError


@pytest.mark.asyncio
async def test_did_resolver_cache_with_web_feed() -> None:
    feed_url = 'feed.atproto.blue'
    did_web = f'did:web:{feed_url}'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)
    did_doc = await resolver.ensure_resolve(did_web)

    expected_object_id = id(did_doc)

    for _ in range(10):
        new_did_doc = await resolver.ensure_resolve(did_web)
        # Check that the object is cached (same object id)
        assert expected_object_id == id(new_did_doc)

    cached_result = await cache.get(did_web)
    assert cached_result is not None
    cached_did_doc = cached_result.document
    assert cached_did_doc is did_doc


@pytest.mark.asyncio
async def test_did_resolver_cache_with_did_plc() -> None:
    did_plc = 'did:plc:kvwvcn5iqfooopmyzvb4qzba'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)
    did_doc = await resolver.ensure_resolve(did_plc)

    expected_object_id = id(did_doc)
    for _ in range(10):
        new_did_doc = await resolver.ensure_resolve(did_plc)
        # Check that the object is cached (same object id)
        assert expected_object_id == id(new_did_doc)

    cached_result = await cache.get(did_plc)
    assert cached_result is not None
    cached_did_doc = cached_result.document
    assert cached_did_doc is did_doc


@pytest.mark.asyncio
async def test_did_resolver_cache_with_unknown_did_plc() -> None:
    did_plc = 'did:plc:kvwvcn5iqfooopmyzvb41234'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)

    assert await resolver.resolve(did_plc) is None
    with pytest.raises(DidNotFoundError):
        await resolver.ensure_resolve(did_plc)

    assert await cache.get(did_plc) is None


@pytest.mark.asyncio
async def test_did_resolver_resolve_no_cache() -> None:
    feed_url = 'feed.atproto.blue'
    did_web = f'did:web:{feed_url}'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)

    cached_did_doc = await resolver.ensure_resolve(did_web)
    new_did_doc = await resolver.resolve_no_cache(did_web)

    assert id(cached_did_doc) != id(new_did_doc)


@pytest.mark.asyncio
async def test_did_resolver_resolve_force() -> None:
    feed_url = 'feed.atproto.blue'
    did_web = f'did:web:{feed_url}'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)

    cached_did_doc = await resolver.ensure_resolve(did_web)
    new_did_doc = await resolver.ensure_resolve(did_web, force_refresh=True)

    assert id(cached_did_doc) != id(new_did_doc)


@pytest.mark.asyncio
async def test_did_resolver_refresh_cache() -> None:
    feed_url = 'feed.atproto.blue'
    did_web = f'did:web:{feed_url}'

    cache = AsyncDidInMemoryCache()
    resolver = AsyncDidResolver(cache=cache)

    cached_did_doc = await resolver.ensure_resolve(did_web)
    await resolver.refresh_cache(did_web)
    new_did_doc = await resolver.ensure_resolve(did_web)

    assert id(cached_did_doc) != id(new_did_doc)
