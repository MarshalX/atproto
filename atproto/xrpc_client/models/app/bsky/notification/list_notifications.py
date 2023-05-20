##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.notification.listNotifications`.

    Attributes:
        limit: Limit.
        cursor: Cursor.
        seenAt: Seen at.
    """

    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None
    seenAt: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.listNotifications`.

    Attributes:
        cursor: Cursor.
        notifications: Notifications.
    """

    notifications: t.List['models.AppBskyNotificationListNotifications.Notification']
    cursor: t.Optional[str] = None


@dataclass
class Notification(base.ModelBase):

    """Definition model for :obj:`app.bsky.notification.listNotifications`.

    Attributes:
        uri: Uri.
        cid: Cid.
        author: Author.
        reason: Expected values are 'like', 'repost', 'follow', 'mention', 'reply', and 'quote'.
        reasonSubject: Reason subject.
        record: Record.
        isRead: Is read.
        indexedAt: Indexed at.
        labels: Labels.
    """

    author: 'models.AppBskyActorDefs.ProfileView'
    cid: str
    indexedAt: str
    isRead: bool
    reason: str
    record: 'base.RecordModelBase'
    uri: str
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None
    reasonSubject: t.Optional[str] = None

    _type: str = 'app.bsky.notification.listNotifications#notification'
