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


class Member(base.ModelBase):
    """Definition model for :obj:`tools.ozone.team.defs`."""

    did: str  #: Did.
    role: t.Union[
        'models.ToolsOzoneTeamDefs.RoleAdmin',
        'models.ToolsOzoneTeamDefs.RoleModerator',
        'models.ToolsOzoneTeamDefs.RoleTriage',
        str,
    ]  #: Role.
    created_at: t.Optional[str] = None  #: Created at.
    disabled: t.Optional[bool] = None  #: Disabled.
    last_updated_by: t.Optional[str] = None  #: Last updated by.
    profile: t.Optional['models.AppBskyActorDefs.ProfileViewDetailed'] = None  #: Profile.
    updated_at: t.Optional[str] = None  #: Updated at.

    py_type: t.Literal['tools.ozone.team.defs#member'] = Field(
        default='tools.ozone.team.defs#member', alias='$type', frozen=True
    )


RoleAdmin = t.Literal[
    'tools.ozone.team.defs#roleAdmin'
]  #: Admin role. Highest level of access, can perform all actions.

RoleModerator = t.Literal['tools.ozone.team.defs#roleModerator']  #: Moderator role. Can perform most actions.

RoleTriage = t.Literal[
    'tools.ozone.team.defs#roleTriage'
]  #: Triage role. Mostly intended for monitoring and escalating issues.
