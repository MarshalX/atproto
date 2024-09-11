##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.notification.listNotifications`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    priority: t.Optional[bool] = None  #: Priority.
    seen_at: t.Optional[str] = None  #: Seen at.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    priority: te.NotRequired[t.Optional[bool]]  #: Priority.
    seen_at: te.NotRequired[t.Optional[str]]  #: Seen at.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.notification.listNotifications`."""

    notifications: t.List['models.AppBskyNotificationListNotifications.Notification']  #: Notifications.
    cursor: t.Optional[str] = None  #: Cursor.
    priority: t.Optional[bool] = None  #: Priority.
    seen_at: t.Optional[str] = None  #: Seen at.


class Notification(base.ModelBase):
    """Definition model for :obj:`app.bsky.notification.listNotifications`."""

    author: 'models.AppBskyActorDefs.ProfileView'  #: Author.
    cid: str  #: Cid.
    indexed_at: str  #: Indexed at.
    is_read: bool  #: Is read.
    reason: t.Union[
        t.Literal['like'],
        t.Literal['repost'],
        t.Literal['follow'],
        t.Literal['mention'],
        t.Literal['reply'],
        t.Literal['quote'],
        t.Literal['starterpack-joined'],
        str,
    ]  #: Expected values are 'like', 'repost', 'follow', 'mention', 'reply', 'quote', and 'starterpack-joined'.
    record: 'UnknownType'  #: Record.
    uri: str  #: Uri.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.
    reason_subject: t.Optional[str] = None  #: Reason subject.

    py_type: t.Literal['app.bsky.notification.listNotifications#notification'] = Field(
        default='app.bsky.notification.listNotifications#notification', alias='$type', frozen=True
    )
