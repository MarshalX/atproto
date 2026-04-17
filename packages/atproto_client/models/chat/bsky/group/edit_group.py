##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.editGroup`."""

    convo_id: str  #: Convo id.
    name: str = Field(min_length=1, max_length=1280)  #: Name.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.
    name: str  #: Name.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.editGroup`."""

    convo: 'models.ChatBskyConvoDefs.ConvoView'  #: Convo.
