import typing as t

from atproto_client import models
from atproto_client.models.utils import get_model_as_dict, get_or_create

from atproto_jetstream.archive.downloader import ArchiveDownloader, AsyncArchiveDownloader, ByteMeter
from atproto_jetstream.archive.engine import SweepState, sweep_archive, sweep_archive_async
from atproto_jetstream.archive.live_bridge import iter_live, iter_live_async
from atproto_jetstream.archive.matcher import RowMatcher
from atproto_jetstream.archive.planner import PlanFilters
from atproto_jetstream.client import _AsyncJetstreamClient, _JetstreamClient
from atproto_jetstream.exceptions import JetstreamError
from atproto_jetstream.models import SubscribeEventsMessage, parse_subscribe_events_message

__all__ = [
    'AsyncJetstreamClient',
    'JetstreamClient',
    'SubscribeEventsMessage',
    'parse_subscribe_events_message',
]

_BASE_WEBSOCKET_URI = 'wss://jetstream.us-east.bsky.network/xrpc'
_METHOD = 'network.bsky.jetstream.subscribeEvents'

#: A narrow filter can idle for a long time; raise it when subscribing to a few DIDs.
_DEFAULT_RECV_TIMEOUT = 60.0

_COMMIT_KIND = 'commit'

Params = models.NetworkBskyJetstreamSubscribeEvents.Params
ParamsDict = models.NetworkBskyJetstreamSubscribeEvents.ParamsDict


def _plan_filters(params: t.Optional[t.Dict[str, t.Any]]) -> PlanFilters:
    params = params or {}

    return PlanFilters(
        kinds=list(params.get('kinds') or ()),
        dids=list(params.get('dids') or ()),
        collections=list(params.get('collections') or ()),
    )


def _row_matcher(params: t.Optional[t.Dict[str, t.Any]], after_seq: int, before_seq: t.Optional[int]) -> RowMatcher:
    params = params or {}

    return RowMatcher(
        kinds=params.get('kinds'),
        dids=params.get('dids'),
        collections=params.get('collections'),
        after_seq=after_seq,
        before_seq=before_seq,
    )


def _build_params(params: t.Optional[t.Union[Params, ParamsDict]]) -> t.Optional[t.Dict[str, t.Any]]:
    params_model = t.cast('t.Optional[Params]', get_or_create(params, Params))
    if params_model is None:
        return None

    if params_model.collections and params_model.kinds and _COMMIT_KIND not in params_model.kinds:
        # The server rejects this pre-upgrade; fail before dialing with a clearer message.
        raise JetstreamError('The "collections" filter applies to commits only, but "kinds" excludes them')

    return get_model_as_dict(params_model)


class JetstreamClient(_JetstreamClient):
    """Jetstream v2 client.

    Note:
        Only the v2 wire is supported. Legacy v1 hosts (``jetstream1.*``, ``jetstream2.*``) will not work.

    Note:
        The cursor is tracked for you. Reconnects resume from the last delivered event
        and redelivered events are dropped. Persist :attr:`cursor` to resume across restarts.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://jetstream.us-east.bsky.network/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 60 seconds.
        compress: Receive compressed frames. Falls back to an uncompressed stream
            if the server does not cooperate. Default is :obj:`True`.
        api_key: Archive credential, obtainable at https://bsky.network/account. Used only by
            :obj:`snapshot` and :obj:`replay`; never sent on the websocket. The live tail
            needs no key.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[Params, ParamsDict]] = None,
        base_uri: str = _BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _DEFAULT_RECV_TIMEOUT,
        compress: bool = True,
        api_key: t.Optional[str] = None,
    ) -> None:
        super().__init__(
            method=_METHOD,
            base_uri=base_uri,
            params=_build_params(params),
            recv_timeout=recv_timeout,
            compress=compress,
        )

        self._api_key = api_key
        self._meter = ByteMeter()

    @property
    def bytes_downloaded(self) -> int:
        """:obj:`int`: Archive bytes downloaded. Jetstream meters usage in bytes, not requests."""
        return self._meter.total

    def _archive_downloader(self) -> ArchiveDownloader:
        if not self._api_key:
            raise JetstreamError('An api_key is required to read the archive')

        return ArchiveDownloader(self._http_origin, self._api_key, self._meter)

    def snapshot(
        self,
        after_seq: int = 0,
        before_seq: t.Optional[int] = None,
        *,
        with_cid: bool = True,
    ) -> t.Iterator[SubscribeEventsMessage]:
        """Replay the sealed archive, then stop.

        Note:
            A point-in-time view: rows still in the unsealed active segment are not included.
            Use :obj:`replay` to continue into the live tail instead.

        Args:
            after_seq: Exclusive lower bound. 0 means the whole archive.
            before_seq: Inclusive upper bound.
            with_cid: Derive each record's CID. Skipping it saves a hash per record.

        Yields:
            :obj:`SubscribeEventsMessage`: The same models the live tail delivers.
        """
        state = SweepState(after_seq)
        yield from sweep_archive(
            self._archive_downloader(),
            _plan_filters(self._params),
            _row_matcher(self._params, after_seq, before_seq),
            state,
            after_seq=after_seq,
            before_seq=before_seq,
            with_cid=with_cid,
        )

    def replay(
        self,
        after_seq: int = 0,
        *,
        with_cid: bool = True,
    ) -> t.Iterator[SubscribeEventsMessage]:
        """Replay the archive, then cut over to the live tail without a gap.

        Note:
            Never terminates: it becomes the live tail once the archive is consumed.

        Args:
            after_seq: Exclusive lower bound. 0 means the whole archive.
            with_cid: Derive each record's CID for archived events.

        Yields:
            :obj:`SubscribeEventsMessage`: The same models the live tail delivers.
        """
        state = SweepState(after_seq)
        yield from sweep_archive(
            self._archive_downloader(),
            _plan_filters(self._params),
            _row_matcher(self._params, after_seq, None),
            state,
            after_seq=after_seq,
            with_cid=with_cid,
        )

        # resume inclusively from the seam; the client dedups the overlap
        self._set_param('cursor', state.cutover_seq)
        self._cursor = state.cutover_seq
        yield from iter_live(self)


class AsyncJetstreamClient(_AsyncJetstreamClient):
    """Async jetstream v2 client.

    Note:
        Only the v2 wire is supported. Legacy v1 hosts (``jetstream1.*``, ``jetstream2.*``) will not work.

    Note:
        The cursor is tracked for you. Reconnects resume from the last delivered event
        and redelivered events are dropped. Persist :attr:`cursor` to resume across restarts.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://jetstream.us-east.bsky.network/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 60 seconds.
        compress: Receive compressed frames. Falls back to an uncompressed stream
            if the server does not cooperate. Default is :obj:`True`.
        api_key: Archive credential, obtainable at https://bsky.network/account. Used only by
            :obj:`snapshot` and :obj:`replay`; never sent on the websocket. The live tail
            needs no key.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[Params, ParamsDict]] = None,
        base_uri: str = _BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _DEFAULT_RECV_TIMEOUT,
        compress: bool = True,
        api_key: t.Optional[str] = None,
    ) -> None:
        super().__init__(
            method=_METHOD,
            base_uri=base_uri,
            params=_build_params(params),
            recv_timeout=recv_timeout,
            compress=compress,
        )

        self._api_key = api_key
        self._meter = ByteMeter()

    @property
    def bytes_downloaded(self) -> int:
        """:obj:`int`: Archive bytes downloaded. Jetstream meters usage in bytes, not requests."""
        return self._meter.total

    def _archive_downloader(self) -> AsyncArchiveDownloader:
        if not self._api_key:
            raise JetstreamError('An api_key is required to read the archive')

        return AsyncArchiveDownloader(self._http_origin, self._api_key, self._meter)

    async def snapshot(
        self,
        after_seq: int = 0,
        before_seq: t.Optional[int] = None,
        *,
        with_cid: bool = True,
    ) -> t.AsyncIterator[SubscribeEventsMessage]:
        """Replay the sealed archive, then stop.

        Note:
            A point-in-time view: rows still in the unsealed active segment are not included.
            Use :obj:`replay` to continue into the live tail instead.

        Args:
            after_seq: Exclusive lower bound. 0 means the whole archive.
            before_seq: Inclusive upper bound.
            with_cid: Derive each record's CID. Skipping it saves a hash per record.

        Yields:
            :obj:`SubscribeEventsMessage`: The same models the live tail delivers.
        """
        state = SweepState(after_seq)
        async for message in sweep_archive_async(
            self._archive_downloader(),
            _plan_filters(self._params),
            _row_matcher(self._params, after_seq, before_seq),
            state,
            after_seq=after_seq,
            before_seq=before_seq,
            with_cid=with_cid,
        ):
            yield message

    async def replay(
        self,
        after_seq: int = 0,
        *,
        with_cid: bool = True,
    ) -> t.AsyncIterator[SubscribeEventsMessage]:
        """Replay the archive, then cut over to the live tail without a gap.

        Note:
            Never terminates: it becomes the live tail once the archive is consumed.

        Args:
            after_seq: Exclusive lower bound. 0 means the whole archive.
            with_cid: Derive each record's CID for archived events.

        Yields:
            :obj:`SubscribeEventsMessage`: The same models the live tail delivers.
        """
        state = SweepState(after_seq)
        async for message in sweep_archive_async(
            self._archive_downloader(),
            _plan_filters(self._params),
            _row_matcher(self._params, after_seq, None),
            state,
            after_seq=after_seq,
            with_cid=with_cid,
        ):
            yield message

        # resume inclusively from the seam; the client dedups the overlap
        self._set_param('cursor', state.cutover_seq)
        self._cursor = state.cutover_seq
        async for live_message in iter_live_async(self):
            yield live_message
