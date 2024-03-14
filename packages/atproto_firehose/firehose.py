import typing as t

from atproto_client import models
from atproto_client.models.utils import get_model_as_dict, get_or_create

from atproto_firehose.client import AsyncFirehoseClient, FirehoseClient

if t.TYPE_CHECKING:
    from atproto_firehose.models import MessageFrame

_REPOS_BASE_WEBSOCKET_URI = 'wss://bsky.network/xrpc'
_LABELS_BASE_WEBSOCKET_URI = 'wss://mod.bsky.app/xrpc'

# TODO(MarshalX): Everything here could be autogenerated from the lexicon.
_SUBSCRIBE_REPOS_MESSAGE_TYPE_TO_MODEL = {
    '#commit': models.ComAtprotoSyncSubscribeRepos.Commit,
    '#handle': models.ComAtprotoSyncSubscribeRepos.Handle,
    '#migrate': models.ComAtprotoSyncSubscribeRepos.Migrate,
    '#tombstone': models.ComAtprotoSyncSubscribeRepos.Tombstone,
    '#info': models.ComAtprotoSyncSubscribeRepos.Info,
    '#identity': models.ComAtprotoSyncSubscribeRepos.Identity,
}
_SUBSCRIBE_LABELS_MESSAGE_TYPE_TO_MODEL = {
    '#labels': models.ComAtprotoLabelSubscribeLabels.Labels,
    '#info': models.ComAtprotoLabelSubscribeLabels.Info,
}

#: Subscribe Repos Message
SubscribeReposMessage = t.Union[
    models.ComAtprotoSyncSubscribeRepos.Commit,
    models.ComAtprotoSyncSubscribeRepos.Handle,
    models.ComAtprotoSyncSubscribeRepos.Migrate,
    models.ComAtprotoSyncSubscribeRepos.Tombstone,
    models.ComAtprotoSyncSubscribeRepos.Info,
    models.ComAtprotoSyncSubscribeRepos.Identity,
]
#: Subscribe Labels Message
SubscribeLabelsMessage = t.Union[
    models.ComAtprotoLabelSubscribeLabels.Labels,
    models.ComAtprotoLabelSubscribeLabels.Info,
]


def parse_subscribe_repos_message(message: 'MessageFrame') -> SubscribeReposMessage:
    """Parse Firehose repositories message to the corresponding model.

    Note:
        Use `decode_inner_cbor` only when required to increase performance.

    Args:
        message: Message frame.

    Returns:
        :obj:`SubscribeReposMessage`: Corresponding message model.
    """
    model_class = _SUBSCRIBE_REPOS_MESSAGE_TYPE_TO_MODEL[message.type]
    return get_or_create(message.body, model_class)


def parse_subscribe_labels_message(message: 'MessageFrame') -> SubscribeLabelsMessage:
    """Parse Firehose labels message to the corresponding model.

    Args:
        message: Message frame.

    Returns:
        :obj:`SubscribeLabelsMessage`: Corresponding message model.
    """
    model_class = _SUBSCRIBE_LABELS_MESSAGE_TYPE_TO_MODEL[message.type]
    return get_or_create(message.body, model_class)


class FirehoseSubscribeReposClient(FirehoseClient):
    """Firehose subscribe repos client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        base_uri: t.Optional[str] = _REPOS_BASE_WEBSOCKET_URI,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoSyncSubscribeRepos.Params)

        params_dict = None
        if params_model:
            params_dict = get_model_as_dict(params_model)

        super().__init__(method='com.atproto.sync.subscribeRepos', base_uri=base_uri, params=params_dict)


class AsyncFirehoseSubscribeReposClient(AsyncFirehoseClient):
    """Async firehose subscribe repos client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        base_uri: t.Optional[str] = _REPOS_BASE_WEBSOCKET_URI,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoSyncSubscribeRepos.Params)

        params_dict = None
        if params_model:
            params_dict = get_model_as_dict(params_model)

        super().__init__(method='com.atproto.sync.subscribeRepos', base_uri=base_uri, params=params_dict)


# TODO(MarshalX): SubscribeLabels doesn't work yet? HTTP 502 Error


class FirehoseSubscribeLabelsClient(FirehoseClient):
    """Firehose subscribe labels client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        base_uri: t.Optional[str] = _LABELS_BASE_WEBSOCKET_URI,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoLabelSubscribeLabels.Params)

        params_dict = None
        if params_model:
            params_dict = get_model_as_dict(params_model)

        super().__init__(method='com.atproto.label.subscribeLabels', base_uri=base_uri, params=params_dict)


class AsyncFirehoseSubscribeLabelsClient(AsyncFirehoseClient):
    """Async firehose subscribe labels client.

    Args:
        params: Parameters model.
        base_uri: Base websocket URI. Example: `wss://bsky.social/xrpc`.
    """

    def __init__(
        self,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        base_uri: t.Optional[str] = _LABELS_BASE_WEBSOCKET_URI,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoLabelSubscribeLabels.Params)

        params_dict = None
        if params_model:
            params_dict = get_model_as_dict(params_model)

        super().__init__(method='com.atproto.label.subscribeLabels', base_uri=base_uri, params=params_dict)
