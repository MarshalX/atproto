#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_subscription.client import AsyncSubscriptionClient, SubscriptionClient

from atproto_client import models
from atproto_client.models.utils import get_model_as_dict, get_or_create

if t.TYPE_CHECKING:
    from atproto_subscription.frames import MessageFrame

#: Messages of the ``chat.bsky.moderation.subscribeModEvents`` subscription.
ChatBskyModerationSubscribeModEventsMessage = t.Union[
    'models.ChatBskyModerationSubscribeModEvents.EventConvoFirstMessage',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatCreated',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberAdded',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberJoined',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequest',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequestApproved',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequestRejected',
    'models.ChatBskyModerationSubscribeModEvents.EventChatAccepted',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberLeft',
    'models.ChatBskyModerationSubscribeModEvents.EventGroupChatUpdated',
    'models.ChatBskyModerationSubscribeModEvents.EventRateLimitExceeded',
]
CHAT_BSKY_MODERATION_SUBSCRIBE_MOD_EVENTS_MESSAGE_TYPE_TO_MODEL = {
    '#eventConvoFirstMessage': models.ChatBskyModerationSubscribeModEvents.EventConvoFirstMessage,
    '#eventGroupChatCreated': models.ChatBskyModerationSubscribeModEvents.EventGroupChatCreated,
    '#eventGroupChatMemberAdded': models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberAdded,
    '#eventGroupChatMemberJoined': models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberJoined,
    '#eventGroupChatJoinRequest': models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequest,
    '#eventGroupChatJoinRequestApproved': models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequestApproved,
    '#eventGroupChatJoinRequestRejected': models.ChatBskyModerationSubscribeModEvents.EventGroupChatJoinRequestRejected,
    '#eventChatAccepted': models.ChatBskyModerationSubscribeModEvents.EventChatAccepted,
    '#eventGroupChatMemberLeft': models.ChatBskyModerationSubscribeModEvents.EventGroupChatMemberLeft,
    '#eventGroupChatUpdated': models.ChatBskyModerationSubscribeModEvents.EventGroupChatUpdated,
    '#eventRateLimitExceeded': models.ChatBskyModerationSubscribeModEvents.EventRateLimitExceeded,
}


def parse_chat_bsky_moderation_subscribe_mod_events_message(
    message: 'MessageFrame',
) -> 'ChatBskyModerationSubscribeModEventsMessage':
    """Parse a message frame of ``chat.bsky.moderation.subscribeModEvents`` into its model.

    Args:
        message: Message frame.

    Returns:
        :obj:`.ChatBskyModerationSubscribeModEventsMessage`: Corresponding message model.
    """
    return t.cast(
        'ChatBskyModerationSubscribeModEventsMessage',
        get_or_create(message.body, CHAT_BSKY_MODERATION_SUBSCRIBE_MOD_EVENTS_MESSAGE_TYPE_TO_MODEL[message.type]),
    )


class ChatBskyModerationSubscribeModEventsClient(SubscriptionClient):
    """Client of the ``chat.bsky.moderation.subscribeModEvents`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ChatBskyModerationSubscribeModEvents.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ChatBskyModerationSubscribeModEvents.Params)
        super().__init__(
            method='chat.bsky.moderation.subscribeModEvents',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


class AsyncChatBskyModerationSubscribeModEventsClient(AsyncSubscriptionClient):
    """Client of the ``chat.bsky.moderation.subscribeModEvents`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ChatBskyModerationSubscribeModEvents.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ChatBskyModerationSubscribeModEvents.Params)
        super().__init__(
            method='chat.bsky.moderation.subscribeModEvents',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


#: Messages of the ``com.atproto.label.subscribeLabels`` subscription.
ComAtprotoLabelSubscribeLabelsMessage = t.Union[
    'models.ComAtprotoLabelSubscribeLabels.Labels',
    'models.ComAtprotoLabelSubscribeLabels.Info',
]
COM_ATPROTO_LABEL_SUBSCRIBE_LABELS_MESSAGE_TYPE_TO_MODEL = {
    '#labels': models.ComAtprotoLabelSubscribeLabels.Labels,
    '#info': models.ComAtprotoLabelSubscribeLabels.Info,
}


def parse_com_atproto_label_subscribe_labels_message(
    message: 'MessageFrame',
) -> 'ComAtprotoLabelSubscribeLabelsMessage':
    """Parse a message frame of ``com.atproto.label.subscribeLabels`` into its model.

    Args:
        message: Message frame.

    Returns:
        :obj:`.ComAtprotoLabelSubscribeLabelsMessage`: Corresponding message model.
    """
    return t.cast(
        'ComAtprotoLabelSubscribeLabelsMessage',
        get_or_create(message.body, COM_ATPROTO_LABEL_SUBSCRIBE_LABELS_MESSAGE_TYPE_TO_MODEL[message.type]),
    )


class ComAtprotoLabelSubscribeLabelsClient(SubscriptionClient):
    """Client of the ``com.atproto.label.subscribeLabels`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoLabelSubscribeLabels.Params)
        super().__init__(
            method='com.atproto.label.subscribeLabels',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


class AsyncComAtprotoLabelSubscribeLabelsClient(AsyncSubscriptionClient):
    """Client of the ``com.atproto.label.subscribeLabels`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoLabelSubscribeLabels.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoLabelSubscribeLabels.Params)
        super().__init__(
            method='com.atproto.label.subscribeLabels',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


#: Messages of the ``com.atproto.sync.subscribeRepos`` subscription.
ComAtprotoSyncSubscribeReposMessage = t.Union[
    'models.ComAtprotoSyncSubscribeRepos.Commit',
    'models.ComAtprotoSyncSubscribeRepos.Sync',
    'models.ComAtprotoSyncSubscribeRepos.Identity',
    'models.ComAtprotoSyncSubscribeRepos.Account',
    'models.ComAtprotoSyncSubscribeRepos.Info',
]
COM_ATPROTO_SYNC_SUBSCRIBE_REPOS_MESSAGE_TYPE_TO_MODEL = {
    '#commit': models.ComAtprotoSyncSubscribeRepos.Commit,
    '#sync': models.ComAtprotoSyncSubscribeRepos.Sync,
    '#identity': models.ComAtprotoSyncSubscribeRepos.Identity,
    '#account': models.ComAtprotoSyncSubscribeRepos.Account,
    '#info': models.ComAtprotoSyncSubscribeRepos.Info,
}


def parse_com_atproto_sync_subscribe_repos_message(message: 'MessageFrame') -> 'ComAtprotoSyncSubscribeReposMessage':
    """Parse a message frame of ``com.atproto.sync.subscribeRepos`` into its model.

    Args:
        message: Message frame.

    Returns:
        :obj:`.ComAtprotoSyncSubscribeReposMessage`: Corresponding message model.
    """
    return t.cast(
        'ComAtprotoSyncSubscribeReposMessage',
        get_or_create(message.body, COM_ATPROTO_SYNC_SUBSCRIBE_REPOS_MESSAGE_TYPE_TO_MODEL[message.type]),
    )


class ComAtprotoSyncSubscribeReposClient(SubscriptionClient):
    """Client of the ``com.atproto.sync.subscribeRepos`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoSyncSubscribeRepos.Params)
        super().__init__(
            method='com.atproto.sync.subscribeRepos',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


class AsyncComAtprotoSyncSubscribeReposClient(AsyncSubscriptionClient):
    """Client of the ``com.atproto.sync.subscribeRepos`` subscription.

    Args:
        base_uri: Base websocket URI, ending in ``/xrpc``.
        params: Parameters model.
        recv_timeout: Reconnect after this many seconds of inactivity.
    """

    def __init__(
        self,
        base_uri: str,
        params: t.Optional[t.Union[dict, 'models.ComAtprotoSyncSubscribeRepos.Params']] = None,
        recv_timeout: t.Optional[float] = None,
    ) -> None:
        params_model = get_or_create(params, models.ComAtprotoSyncSubscribeRepos.Params)
        super().__init__(
            method='com.atproto.sync.subscribeRepos',
            base_uri=base_uri,
            params=get_model_as_dict(params_model) if params_model else None,
            recv_timeout=recv_timeout,
        )


#: Messages of the ``network.bsky.jetstream.subscribeEvents`` subscription.
NetworkBskyJetstreamSubscribeEventsMessage = t.Union[
    'models.NetworkBskyJetstreamSubscribeEvents.Commit',
    'models.NetworkBskyJetstreamSubscribeEvents.Identity',
    'models.NetworkBskyJetstreamSubscribeEvents.Account',
    'models.NetworkBskyJetstreamSubscribeEvents.Sync',
    'models.NetworkBskyJetstreamSubscribeEvents.Info',
]
NETWORK_BSKY_JETSTREAM_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL = {
    '#commit': models.NetworkBskyJetstreamSubscribeEvents.Commit,
    '#identity': models.NetworkBskyJetstreamSubscribeEvents.Identity,
    '#account': models.NetworkBskyJetstreamSubscribeEvents.Account,
    '#sync': models.NetworkBskyJetstreamSubscribeEvents.Sync,
    '#info': models.NetworkBskyJetstreamSubscribeEvents.Info,
}


def parse_network_bsky_jetstream_subscribe_events_message(
    message: 'MessageFrame',
) -> 'NetworkBskyJetstreamSubscribeEventsMessage':
    """Parse a message frame of ``network.bsky.jetstream.subscribeEvents`` into its model.

    Args:
        message: Message frame.

    Returns:
        :obj:`.NetworkBskyJetstreamSubscribeEventsMessage`: Corresponding message model.
    """
    return t.cast(
        'NetworkBskyJetstreamSubscribeEventsMessage',
        get_or_create(message.body, NETWORK_BSKY_JETSTREAM_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL[message.type]),
    )
