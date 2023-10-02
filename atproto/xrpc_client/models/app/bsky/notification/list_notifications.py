##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.notification.listNotifications`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    seen_at: t.Optional[str] = Field(default=None, alias='seenAt')  #: Seen at.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    seen_at: te.NotRequired[t.Optional[str]]  #: Seen at.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.notification.listNotifications`."""

    notifications: t.List['models.AppBskyNotificationListNotifications.Notification']  #: Notifications.
    cursor: t.Optional[str] = None  #: Cursor.


class Notification(base.ModelBase):

    """Definition model for :obj:`app.bsky.notification.listNotifications`."""

    author: 'models.AppBskyActorDefs.ProfileView'  #: Author.
    cid: str  #: Cid.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    is_read: bool = Field(alias='isRead')  #: Is read.
    reason: str  #: Expected values are 'like', 'repost', 'follow', 'mention', 'reply', and 'quote'.
    record: 'UnknownType'  #: Record.
    uri: str  #: Uri.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    reason_subject: t.Optional[str] = Field(default=None, alias='reasonSubject')  #: Reason subject.

    py_type: te.Literal['app.bsky.notification.listNotifications#notification'] = Field(
        default='app.bsky.notification.listNotifications#notification', alias='$type', frozen=True
    )
