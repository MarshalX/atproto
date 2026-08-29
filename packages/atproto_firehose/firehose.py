import typing as t

from atproto_client.subscriptions import (
    AsyncComAtprotoLabelSubscribeLabelsClient,
    AsyncComAtprotoSyncSubscribeReposClient,
    ComAtprotoLabelSubscribeLabelsClient,
    ComAtprotoSyncSubscribeReposClient,
    parse_com_atproto_label_subscribe_labels_message,
    parse_com_atproto_sync_subscribe_repos_message,
)
from atproto_client.subscriptions import (
    ComAtprotoLabelSubscribeLabelsMessage as SubscribeLabelsMessage,
)
from atproto_client.subscriptions import (
    ComAtprotoSyncSubscribeReposMessage as SubscribeReposMessage,
)

if t.TYPE_CHECKING:
    from atproto_client import models

_REPOS_BASE_WEBSOCKET_URI = 'wss://bsky.network/xrpc'
_LABELS_BASE_WEBSOCKET_URI = 'wss://mod.bsky.app/xrpc'

_REPOS_DEFAULT_RECV_TIMEOUT = 30.0
_LABELS_DEFAULT_RECV_TIMEOUT = 60.0 * 5

#: Parse Firehose repositories message to the corresponding model.
parse_subscribe_repos_message = parse_com_atproto_sync_subscribe_repos_message
#: Parse Firehose labels message to the corresponding model.
parse_subscribe_labels_message = parse_com_atproto_label_subscribe_labels_message


class FirehoseSubscribeReposClient(ComAtprotoSyncSubscribeReposClient):
    """Firehose subscribe repos client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 30 seconds.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        base_uri: t.Optional[str] = _REPOS_BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _REPOS_DEFAULT_RECV_TIMEOUT,
    ) -> None:
        super().__init__(base_uri=base_uri or _REPOS_BASE_WEBSOCKET_URI, params=params, recv_timeout=recv_timeout)


class AsyncFirehoseSubscribeReposClient(AsyncComAtprotoSyncSubscribeReposClient):
    """Async firehose subscribe repos client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 30 seconds.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        base_uri: t.Optional[str] = _REPOS_BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _REPOS_DEFAULT_RECV_TIMEOUT,
    ) -> None:
        super().__init__(base_uri=base_uri or _REPOS_BASE_WEBSOCKET_URI, params=params, recv_timeout=recv_timeout)


class FirehoseSubscribeLabelsClient(ComAtprotoLabelSubscribeLabelsClient):
    """Firehose subscribe labels client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 300 seconds (5 minutes).
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        base_uri: t.Optional[str] = _LABELS_BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _LABELS_DEFAULT_RECV_TIMEOUT,
    ) -> None:
        super().__init__(base_uri=base_uri or _LABELS_BASE_WEBSOCKET_URI, params=params, recv_timeout=recv_timeout)


class AsyncFirehoseSubscribeLabelsClient(AsyncComAtprotoLabelSubscribeLabelsClient):
    """Async firehose subscribe labels client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
        recv_timeout: Reconnect to the server after this many seconds of inactivity.
            Default is 300 seconds (5 minutes).
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        base_uri: t.Optional[str] = _LABELS_BASE_WEBSOCKET_URI,
        recv_timeout: t.Optional[float] = _LABELS_DEFAULT_RECV_TIMEOUT,
    ) -> None:
        super().__init__(base_uri=base_uri or _LABELS_BASE_WEBSOCKET_URI, params=params, recv_timeout=recv_timeout)


__all__ = [
    'AsyncFirehoseSubscribeLabelsClient',
    'AsyncFirehoseSubscribeReposClient',
    'FirehoseSubscribeLabelsClient',
    'FirehoseSubscribeReposClient',
    'SubscribeLabelsMessage',
    'SubscribeReposMessage',
    'parse_subscribe_labels_message',
    'parse_subscribe_repos_message',
]
