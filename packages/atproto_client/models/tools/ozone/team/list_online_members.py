#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.team.listOnlineMembers`."""

    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.


class ParamsDict(t.TypedDict):
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.team.listOnlineMembers`."""

    members: t.List['models.ToolsOzoneTeamListOnlineMembers.OnlineMember'] = Field(max_length=100)  #: Members.


class OnlineMember(base.ModelBase):
    """Definition model for :obj:`tools.ozone.team.listOnlineMembers`."""

    did: string_formats.Did  #: Did.
    last_active: string_formats.DateTime  #: Last active.

    py_type: t.Literal['tools.ozone.team.listOnlineMembers#onlineMember'] = Field(
        default='tools.ozone.team.listOnlineMembers#onlineMember', alias='$type', frozen=True
    )
