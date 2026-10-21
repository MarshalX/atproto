import inspect
import typing as t

import typing_extensions as te
from pydantic import BaseModel

T = t.TypeVar('T')
T_co = t.TypeVar('T_co', covariant=True)
ResponseT = t.TypeVar('ResponseT', bound='PaginatedResponse[t.Any]')
ResponseT_co = t.TypeVar('ResponseT_co', bound='PaginatedResponse[t.Any]', covariant=True)


@te.runtime_checkable
class PaginatedResponse(te.Protocol[T_co]):
    """Response of a cursor-paginated method.

    Every generated ``Response`` model of a query that takes and returns a ``cursor`` implements it.
    """

    @property
    def cursor(self) -> t.Optional[str]: ...

    def get_page_items(self) -> t.Sequence[T_co]: ...


def _get_cursor(params: t.Any) -> t.Optional[str]:
    if isinstance(params, dict):
        return params.get('cursor')
    return getattr(params, 'cursor', None)


def _with_cursor(params: t.Any, cursor: t.Optional[str]) -> t.Any:
    if isinstance(params, BaseModel):
        return params.model_copy(update={'cursor': cursor})
    return {**(params or {}), 'cursor': cursor}


class _PaginatorBase:
    def __init__(
        self, method: t.Callable[..., t.Any], params: t.Any, max_pages: t.Optional[int], kwargs: t.Any
    ) -> None:
        self._method = method
        self._params = params
        self._max_pages = max_pages
        self._kwargs = kwargs

        self._pages = 0
        self._done = False
        self._seen_cursors: t.Set[str] = set()

        #: Cursor of the next page to fetch. ``None`` after the last page.
        self.cursor: t.Optional[str] = _get_cursor(params)
        if self.cursor:
            self._seen_cursors.add(self.cursor)

    def _has_next_page(self) -> bool:
        return not self._done and (self._max_pages is None or self._pages < self._max_pages)

    def _fetch_args(self) -> t.Any:
        return _with_cursor(self._params, self.cursor)

    def _on_page(self, page: t.Any) -> None:
        if not isinstance(page, PaginatedResponse):
            raise TypeError(f'{type(page).__name__} is not a paginated response')

        self._pages += 1
        self.cursor = page.cursor
        # a repeated cursor would loop forever
        if not self.cursor or self.cursor in self._seen_cursors:
            self.cursor = None
            self._done = True
        else:
            self._seen_cursors.add(self.cursor)


class Paginator(_PaginatorBase, t.Generic[ResponseT_co]):
    """Lazy iterator over the pages of a cursor-paginated method. Created by :func:`paginate`.

    Iterating again continues after the last fetched page, so an interrupted loop can be resumed.
    """

    def __iter__(self) -> t.Iterator[ResponseT_co]:
        while self._has_next_page():
            page = self._method(self._fetch_args(), **self._kwargs)
            if inspect.iscoroutine(page):
                page.close()
                raise TypeError('The method returned a coroutine; pass an "async def" function to paginate it')

            self._on_page(page)
            yield page

    def items(self: 'Paginator[PaginatedResponse[T]]') -> t.Iterator[T]:
        """Iterate over the items of all pages."""
        for page in self:
            yield from page.get_page_items()


class AsyncPaginator(_PaginatorBase, t.Generic[ResponseT_co]):
    """Lazy async iterator over the pages of a cursor-paginated method. Created by :func:`paginate`.

    Iterating again continues after the last fetched page, so an interrupted loop can be resumed.
    """

    async def __aiter__(self) -> t.AsyncIterator[ResponseT_co]:
        while self._has_next_page():
            page = await self._method(self._fetch_args(), **self._kwargs)
            self._on_page(page)
            yield page

    async def items(self: 'AsyncPaginator[PaginatedResponse[T]]') -> t.AsyncIterator[T]:
        """Iterate over the items of all pages."""
        async for page in self:
            for item in page.get_page_items():
                yield item


@t.overload
def paginate(
    method: t.Callable[..., t.Awaitable[ResponseT]],
    params: t.Any = None,
    *,
    max_pages: t.Optional[int] = None,
    **kwargs: t.Any,
) -> AsyncPaginator[ResponseT]: ...


@t.overload
def paginate(
    method: t.Callable[..., ResponseT],
    params: t.Any = None,
    *,
    max_pages: t.Optional[int] = None,
    **kwargs: t.Any,
) -> Paginator[ResponseT]: ...


def paginate(
    method: t.Callable[..., t.Any],
    params: t.Any = None,
    *,
    max_pages: t.Optional[int] = None,
    **kwargs: t.Any,
) -> t.Union[Paginator[t.Any], AsyncPaginator[t.Any]]:
    """Iterate over all pages of a cursor-paginated method.

    Pages are fetched lazily, one request per page, until the server returns no cursor
    or ``max_pages`` pages are fetched. Collecting everything can take many requests and hit rate limits.

    Example:
        >>> from atproto import Client, client_utils
        >>> client = Client()
        >>> for profile in client_utils.paginate(client.app.bsky.graph.get_follows, {'actor': 'atproto.com'}).items():
        ...     print(profile.handle)

    Args:
        method: Namespace method of a paginated query, e.g. ``client.app.bsky.graph.get_follows``.
            Async methods return :class:`AsyncPaginator`.
        params: Parameters of the method, as a model or a dict. A ``cursor`` in them sets the first page.
        max_pages: Maximum number of pages to fetch.
        **kwargs: Arbitrary arguments to HTTP request.

    Returns:
        :class:`Paginator` or :class:`AsyncPaginator` over the response models.
        Use ``.items()`` to iterate over the page items instead.
    """
    if inspect.iscoroutinefunction(method):
        return AsyncPaginator(method, params, max_pages, kwargs)
    return Paginator(method, params, max_pages, kwargs)
