"""`detect_facets()` resolves the handles of the mentions. The requests are mocked, like the TypeScript tests do."""

import typing as t

import pytest
from atproto_client import AsyncClient, Client, models
from atproto_client.client.base import AsyncClientBase, ClientBase
from atproto_client.exceptions import BadRequestError, NetworkError
from atproto_client.models.common import XrpcError
from atproto_client.request import Response

_UNRESOLVABLE = 'unresolvable.com'


def _resolve_handle_response(handle: str) -> Response:
    if handle == _UNRESOLVABLE:
        error = XrpcError(error='InvalidRequest', message='Unable to resolve handle')
        raise BadRequestError(Response(success=False, status_code=400, content=error, headers={}))

    return Response(success=True, status_code=200, content={'did': f'did:fake:{handle}'}, headers={})


@pytest.fixture
def resolved_handles(monkeypatch: pytest.MonkeyPatch) -> t.List[str]:
    """Resolve every handle to `did:fake:<handle>`, except `unresolvable.com`. Collects the requested handles."""
    handles: t.List[str] = []

    def fake_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        assert kwargs['url'].endswith('com.atproto.identity.resolveHandle')
        handles.append(kwargs['params'].handle)
        return _resolve_handle_response(kwargs['params'].handle)

    async def fake_async_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        return fake_invoke(self, invoke_type, **kwargs)

    monkeypatch.setattr(ClientBase, '_invoke', fake_invoke)
    monkeypatch.setattr(AsyncClientBase, '_invoke', fake_async_invoke)
    return handles


def _summary(text: str, facets: t.List[models.AppBskyRichtextFacet.Main]) -> t.List[t.Tuple[str, str]]:
    """Return the text each facet covers and the value of its feature (DID, URI or tag)."""
    result = []
    for facet in facets:
        (feature,) = facet.features
        value = {
            models.AppBskyRichtextFacet.Mention: lambda f: f.did,
            models.AppBskyRichtextFacet.Link: lambda f: f.uri,
            models.AppBskyRichtextFacet.Tag: lambda f: f.tag,
        }[type(feature)](feature)
        covered = text.encode()[facet.index.byte_start : facet.index.byte_end].decode()
        result.append((covered, value))
    return result


def test_detect_facets_resolves_mentions(resolved_handles: t.List[str]) -> None:
    text = 'Hey @bsky.app, check #this out: https://example.com $AAPL'

    facets = Client().detect_facets(text)

    assert _summary(text, facets) == [
        ('@bsky.app', 'did:fake:bsky.app'),
        ('#this', 'this'),
        ('https://example.com', 'https://example.com'),
        ('$AAPL', '$AAPL'),
    ]
    assert resolved_handles == ['bsky.app']


def test_detect_facets_sorts_facets_by_position(resolved_handles: t.List[str]) -> None:
    text = '#first @a.com https://b.com @c.com $LAST'

    facets = Client().detect_facets(text)

    assert [covered for covered, _ in _summary(text, facets)] == [
        '#first',
        '@a.com',
        'https://b.com',
        '@c.com',
        '$LAST',
    ]
    assert [facet.index.byte_start for facet in facets] == sorted(facet.index.byte_start for facet in facets)


def test_detect_facets_drops_mentions_that_do_not_resolve(resolved_handles: t.List[str]) -> None:
    text = f'@{_UNRESOLVABLE} @handle.com #tag'

    facets = Client().detect_facets(text)

    assert _summary(text, facets) == [('@handle.com', 'did:fake:handle.com'), ('#tag', 'tag')]
    assert resolved_handles == [_UNRESOLVABLE, 'handle.com']


def test_detect_facets_resolves_each_handle_once(resolved_handles: t.List[str]) -> None:
    text = '@handle.com @handle.com @other.com @handle.com'

    facets = Client().detect_facets(text)

    assert len(facets) == 4
    assert resolved_handles == ['handle.com', 'other.com']


def test_detect_facets_does_not_resolve_anything_without_mentions(resolved_handles: t.List[str]) -> None:
    text = 'No mentions, only #tag and https://example.com'

    assert len(Client().detect_facets(text)) == 2
    assert resolved_handles == []


def test_detect_facets_does_not_hide_other_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        raise NetworkError(Response(success=False, status_code=502, content=None, headers={}))

    monkeypatch.setattr(ClientBase, '_invoke', fake_invoke)

    with pytest.raises(NetworkError):
        Client().detect_facets('@handle.com')


@pytest.mark.asyncio
async def test_async_detect_facets_resolves_mentions(resolved_handles: t.List[str]) -> None:
    text = f'@{_UNRESOLVABLE} @handle.com #tag'

    facets = await AsyncClient().detect_facets(text)

    assert _summary(text, facets) == [('@handle.com', 'did:fake:handle.com'), ('#tag', 'tag')]
    assert resolved_handles == [_UNRESOLVABLE, 'handle.com']
