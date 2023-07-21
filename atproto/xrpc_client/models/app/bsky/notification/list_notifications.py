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

    """Parameters model for :obj:`app.bsky.notification.listNotifications`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = None  #: Limit.
    seenAt: t.Optional[str] = None  #: Seen at.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.listNotifications`."""

    notifications: t.List['models.AppBskyNotificationListNotifications.Notification']  #: Notifications.
    cursor: t.Optional[str] = None  #: Cursor.


@dataclass
class Notification(base.ModelBase):

    """Definition model for :obj:`app.bsky.notification.listNotifications`."""

    author: 'models.AppBskyActorDefs.ProfileView'  #: Author.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    isRead: bool  #: Is read.
    reason: str  #: Expected values are 'like', 'repost', 'follow', 'mention', 'reply', and 'quote'.
    record: 'base.UnknownDict'  #: Record.
    uri: str  #: Uri.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    reasonSubject: t.Optional[str] = None  #: Reason subject.

    _type: str = 'app.bsky.notification.listNotifications#notification'
