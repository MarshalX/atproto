import typing as t

from atproto_client import models
from atproto_client.models.utils import get_model_as_dict, get_or_create

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
    """

    def __init__(
        self,
        params: t.Optional[t.Union[Params, ParamsDict]] = None,
        base_uri: str = _BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _DEFAULT_RECV_TIMEOUT,
        compress: bool = True,
    ) -> None:
        super().__init__(
            method=_METHOD,
            base_uri=base_uri,
            params=_build_params(params),
            recv_timeout=recv_timeout,
            compress=compress,
        )


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
    """

    def __init__(
        self,
        params: t.Optional[t.Union[Params, ParamsDict]] = None,
        base_uri: str = _BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _DEFAULT_RECV_TIMEOUT,
        compress: bool = True,
    ) -> None:
        super().__init__(
            method=_METHOD,
            base_uri=base_uri,
            params=_build_params(params),
            recv_timeout=recv_timeout,
            compress=compress,
        )
