##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`chat.bsky.group.addMembers`."""

    convo_id: str  #: Convo id.
    members: t.List[string_formats.Did] = Field(min_length=1)  #: Members.


class DataDict(t.TypedDict):
    convo_id: str  #: Convo id.
    members: t.List[string_formats.Did]  #: Members.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`chat.bsky.group.addMembers`."""

    convo: 'models.ChatBskyConvoDefs.ConvoView'  #: Convo.
    added_members: t.Optional[t.List['models.ChatBskyActorDefs.ProfileViewBasic']] = None  #: Added members.
