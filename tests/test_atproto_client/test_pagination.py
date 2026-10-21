import typing as t

import pytest
from atproto_client import AsyncClient, Client, models
from atproto_client.client.base import AsyncClientBase, ClientBase
from atproto_client.exceptions import RateLimitExceededError
from atproto_client.request import Response
from atproto_client.utils import AsyncPaginator, Paginator, paginate

_SUBJECT = {'did': 'did:plc:subject', 'handle': 'subject.test'}


class FakeServer:
    """Serve `app.bsky.graph.getFollows` pages keyed by request cursor; record every request."""

    def __init__(self) -> None:
        self.pages: t.Dict[t.Optional[str], t.Tuple[t.List[str], t.Optional[str]]] = {
            None: (['a', 'b'], 'c1'),
            'c1': (['c'], 'c2'),
            'c2': (['d'], None),
        }
        self.requests: t.List[t.Dict[str, t.Any]] = []
        self.fail_once_on: t.Set[t.Optional[str]] = set()

    def handle(self, **kwargs: t.Any) -> Response:
        self.requests.append(kwargs)

        url = kwargs['url']
        if url.endswith('app.bsky.actor.getProfile'):
            return Response(success=True, status_code=200, content=_SUBJECT, headers={})
        assert url.endswith('app.bsky.graph.getFollows')

        cursor = kwargs['params'].cursor
        if cursor in self.fail_once_on:
            self.fail_once_on.remove(cursor)
            raise RateLimitExceededError(Response(success=False, status_code=429, content=None, headers={}))

        handles, next_cursor = self.pages[cursor]
        content = {
            'subject': _SUBJECT,
            'follows': [{'did': f'did:plc:{h}', 'handle': f'{h}.test'} for h in handles],
            'cursor': next_cursor,
        }
        return Response(success=True, status_code=200, content=content, headers={})

    @property
    def cursors(self) -> t.List[t.Optional[str]]:
        return [r['params'].cursor for r in self.requests]


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> FakeServer:
    fake = FakeServer()

    def fake_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        return fake.handle(**kwargs)

    async def fake_async_invoke(self: t.Any, invoke_type: t.Any, **kwargs: t.Any) -> Response:
        return fake.handle(**kwargs)

    monkeypatch.setattr(ClientBase, '_invoke', fake_invoke)
    monkeypatch.setattr(AsyncClientBase, '_invoke', fake_async_invoke)
    return fake


def _handles(profiles: t.Iterable[models.AppBskyActorDefs.ProfileView]) -> t.List[str]:
    return [profile.handle for profile in profiles]


def test_pages(server: FakeServer) -> None:
    pages = list(paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'}))

    assert [_handles(page.follows) for page in pages] == [['a.test', 'b.test'], ['c.test'], ['d.test']]
    assert server.cursors == [None, 'c1', 'c2']


def test_items(server: FakeServer) -> None:
    items = list(paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'}).items())

    assert all(isinstance(item, models.AppBskyActorDefs.ProfileView) for item in items)
    assert _handles(items) == ['a.test', 'b.test', 'c.test', 'd.test']


def test_params_model_is_not_mutated(server: FakeServer) -> None:
    params = models.AppBskyGraphGetFollows.Params(actor='subject.test', limit=2)

    list(paginate(Client().app.bsky.graph.get_follows, params))

    assert params.cursor is None
    assert [r['params'].limit for r in server.requests] == [2, 2, 2]


def test_params_dict_is_not_mutated(server: FakeServer) -> None:
    params: models.AppBskyGraphGetFollows.ParamsDict = {'actor': 'subject.test'}

    list(paginate(Client().app.bsky.graph.get_follows, params))

    assert params == {'actor': 'subject.test'}


def test_starts_from_params_cursor(server: FakeServer) -> None:
    items = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test', 'cursor': 'c1'}).items()

    assert _handles(items) == ['c.test', 'd.test']
    assert server.cursors == ['c1', 'c2']


def test_max_pages(server: FakeServer) -> None:
    paginator = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'}, max_pages=2)

    assert len(list(paginator)) == 2
    assert server.cursors == [None, 'c1']
    assert paginator.cursor == 'c2'


def test_lazy(server: FakeServer) -> None:
    paginator = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'})
    assert server.requests == []

    next(iter(paginator))
    assert server.cursors == [None]


def test_empty_page_with_cursor_does_not_stop(server: FakeServer) -> None:
    server.pages['c1'] = ([], 'c2')

    items = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'}).items()

    assert _handles(items) == ['a.test', 'b.test', 'd.test']


def test_repeated_cursor_stops(server: FakeServer) -> None:
    server.pages['c2'] = (['d'], 'c1')

    paginator = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'})

    assert len(list(paginator)) == 3
    assert paginator.cursor is None


def test_resume_after_error(server: FakeServer) -> None:
    server.fail_once_on.add('c2')
    paginator = paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'})

    fetched = []
    with pytest.raises(RateLimitExceededError):
        fetched.extend(paginator.items())
    fetched.extend(paginator.items())

    assert _handles(fetched) == ['a.test', 'b.test', 'c.test', 'd.test']
    assert server.cursors == [None, 'c1', 'c2', 'c2']


def test_request_kwargs_are_forwarded(server: FakeServer) -> None:
    list(paginate(Client().app.bsky.graph.get_follows, {'actor': 'subject.test'}, headers={'x-test': '1'}))

    assert all(r['headers'] == {'x-test': '1'} for r in server.requests)


def test_not_paginated_method(server: FakeServer) -> None:
    with pytest.raises(TypeError, match='not a paginated response'):
        list(paginate(Client().app.bsky.actor.get_profile, {'actor': 'subject.test'}))  # type: ignore[arg-type]


def test_async_method_returns_async_paginator() -> None:
    assert isinstance(paginate(AsyncClient().app.bsky.graph.get_follows, {'actor': 'a'}), AsyncPaginator)
    assert isinstance(paginate(Client().app.bsky.graph.get_follows, {'actor': 'a'}), Paginator)


def test_sync_paginator_rejects_coroutine(server: FakeServer) -> None:
    client = AsyncClient()

    # typed as AsyncPaginator, but a lambda is not a coroutine function at runtime
    paginator: t.Any = paginate(lambda params: client.app.bsky.graph.get_follows(params), {'actor': 'subject.test'})

    with pytest.raises(TypeError, match='async def'):
        list(paginator)


@pytest.mark.asyncio
async def test_async_pages(server: FakeServer) -> None:
    pages = [page async for page in paginate(AsyncClient().app.bsky.graph.get_follows, {'actor': 'subject.test'})]

    assert [_handles(page.follows) for page in pages] == [['a.test', 'b.test'], ['c.test'], ['d.test']]


@pytest.mark.asyncio
async def test_async_items(server: FakeServer) -> None:
    paginator = paginate(AsyncClient().app.bsky.graph.get_follows, {'actor': 'subject.test'}, max_pages=2)

    items = [item async for item in paginator.items()]

    assert _handles(items) == ['a.test', 'b.test', 'c.test']
    assert paginator.cursor == 'c2'
