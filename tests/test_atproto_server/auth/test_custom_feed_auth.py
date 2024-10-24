import typing as t

import pytest
from atproto import (
    AsyncDidInMemoryCache,
    AsyncIdResolver,
    DidInMemoryCache,
    IdResolver,
    JwtPayload,
    verify_jwt,
    verify_jwt_async,
)

# THESE TESTS ARE NOT MOCKED WITH TEST SERVERS. IT PERFORMS REAL REQUESTS TO THE INTERNET.

HEADER_PREFIX = 'Bearer '

_TEST_JWT_EXPIRED = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpc3MiOiJkaWQ6cGxjOmt2d3ZjbjVpcWZvb29wbXl6dmI0cXpiYSIsImF1ZCI6ImRpZDp3ZWI6ZmVlZC5hdHByb3RvLmJsdWUiLCJleHAiOjE3MDQ4NDExMzh9.50SlT6vw26HsDXVDM4D2D53_Dvzd6bjp3TDc5EyDVD4ob9i3EEB7fmaKE0XR4egMS9Kf9eMdVqH5gJNCaIah4Q'  # noqa: E501
_TEST_AUTHORIZATION_HEADER_VALUE = f'{HEADER_PREFIX}{_TEST_JWT_EXPIRED}'

if t.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class AuthorizationError(Exception): ...


def test_custom_feed_auth_flow(monkeypatch: 'MonkeyPatch') -> None:
    """This is exactly custom feed auth flow."""

    cache = DidInMemoryCache()
    resolver = IdResolver(cache=cache)

    if not _TEST_AUTHORIZATION_HEADER_VALUE.startswith(HEADER_PREFIX):
        raise AuthorizationError('Invalid authorization header')

    jwt = _TEST_AUTHORIZATION_HEADER_VALUE[len(HEADER_PREFIX) :].strip()

    # allow expired token only for tests
    monkeypatch.setattr('atproto_server.auth.jwt._validate_exp', lambda *_: True)

    # should not raise any exception
    jwt_payload = verify_jwt(jwt, resolver.did.resolve_atproto_key)
    assert isinstance(jwt_payload, JwtPayload)


@pytest.mark.asyncio
async def test_custom_feed_auth_flow_async(monkeypatch: 'MonkeyPatch') -> None:
    """This is exactly custom feed auth flow."""

    cache = AsyncDidInMemoryCache()
    resolver = AsyncIdResolver(cache=cache)

    if not _TEST_AUTHORIZATION_HEADER_VALUE.startswith(HEADER_PREFIX):
        raise AuthorizationError('Invalid authorization header')

    jwt = _TEST_AUTHORIZATION_HEADER_VALUE[len(HEADER_PREFIX) :].strip()

    # allow expired token only for tests
    monkeypatch.setattr('atproto_server.auth.jwt._validate_exp', lambda *_: True)

    # should not raise any exception
    jwt_payload = await verify_jwt_async(jwt, resolver.did.resolve_atproto_key)
    assert isinstance(jwt_payload, JwtPayload)
