##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Option(base.ModelBase):
    """Definition model for :obj:`tools.ozone.setting.defs`."""

    created_by: str  #: Created by.
    did: str  #: Did.
    key: str  #: Key.
    last_updated_by: str  #: Last updated by.
    scope: t.Union[t.Literal['instance'], t.Literal['personal'], str]  #: Scope.
    value: 'UnknownType'  #: Value.
    created_at: t.Optional[str] = None  #: Created at.
    description: t.Optional[str] = Field(default=None, max_length=10240)  #: Description.
    manager_role: t.Optional[
        t.Union[
            'models.ToolsOzoneTeamDefs.RoleModerator',
            'models.ToolsOzoneTeamDefs.RoleTriage',
            'models.ToolsOzoneTeamDefs.RoleAdmin',
            str,
        ]
    ] = None  #: Manager role.
    updated_at: t.Optional[str] = None  #: Updated at.

    py_type: t.Literal['tools.ozone.setting.defs#option'] = Field(
        default='tools.ozone.setting.defs#option', alias='$type', frozen=True
    )
