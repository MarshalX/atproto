#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.memberspace.putMembers`."""

    members: t.List['models.ComAtprotoMemberspaceDefs.Member'] = Field(max_length=100)  #: Members.
    space: string_formats.SpaceRef  #: Space.


class DataDict(t.TypedDict):
    members: t.List['models.ComAtprotoMemberspaceDefs.Member']  #: Members.
    space: string_formats.SpaceRef  #: Space.
