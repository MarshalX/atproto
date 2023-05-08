##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

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

    cursor: Optional[str] = None
    limit: Optional[int] = None
    seenAt: Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.listNotifications`.

    Attributes:
        cursor: Cursor.
        notifications: Notifications.
    """

    notifications: List['models.AppBskyNotificationListNotifications.Notification']
    cursor: Optional[str] = None


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
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None
    reasonSubject: Optional[str] = None
