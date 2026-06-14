#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`chat.bsky.convo.getUnreadCounts`."""

    include_group_chats: t.Optional[bool] = True  #: When false, group convos are excluded from the counts.


class ParamsDict(t.TypedDict):
    include_group_chats: te.NotRequired[t.Optional[bool]]  #: When false, group convos are excluded from the counts.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.convo.getUnreadCounts`."""

    unread_accepted_convos: int  #: Number of unread, unlocked accepted convos. Counts convos with unread messages and unread join requests. Capped at 31, where 31 means more than 30.
    unread_request_convos: int  #: Number of unread, unlocked request convos. Includes convos with unread messages, but not with unread join request, since only the owner of a group has join requests to read, and the group would necessarily be accepted. Capped at 11, where 11 means more than 10.
