##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.requestJoin`."""

    code: str  #: Code.


class DataDict(t.TypedDict):
    code: str  #: Code.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.requestJoin`."""

    status: t.Union[t.Literal['joined'], t.Literal['pending'], str]  #: Status.
    convo: t.Optional['models.ChatBskyConvoDefs.ConvoView'] = (
        None  #: The group convo joined. This is only present in the case of status=joined.
    )
