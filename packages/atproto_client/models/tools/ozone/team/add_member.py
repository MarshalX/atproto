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
    """Input data model for :obj:`tools.ozone.team.addMember`."""

    did: str  #: Did.
    role: t.Union[
        'models.ToolsOzoneTeamDefs.RoleAdmin',
        'models.ToolsOzoneTeamDefs.RoleModerator',
        'models.ToolsOzoneTeamDefs.RoleTriage',
        str,
    ]  #: Role.


class DataDict(t.TypedDict):
    did: str  #: Did.
    role: t.Union[
        'models.ToolsOzoneTeamDefs.RoleAdmin',
        'models.ToolsOzoneTeamDefs.RoleModerator',
        'models.ToolsOzoneTeamDefs.RoleTriage',
        str,
    ]  #: Role.
