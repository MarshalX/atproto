##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.listAppPasswords`."""

    passwords: t.List['models.ComAtprotoServerListAppPasswords.AppPassword']  #: Passwords.


class AppPassword(base.ModelBase):
    """Definition model for :obj:`com.atproto.server.listAppPasswords`."""

    created_at: str  #: Created at.
    name: str  #: Name.

    py_type: te.Literal['com.atproto.server.listAppPasswords#appPassword'] = Field(
        default='com.atproto.server.listAppPasswords#appPassword', alias='$type', frozen=True
    )
