##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Set(base.ModelBase):
    """Definition model for :obj:`tools.ozone.set.defs`."""

    name: str = Field(min_length=3, max_length=128)  #: Name.
    description: t.Optional[str] = Field(default=None, max_length=10240)  #: Description.

    py_type: t.Literal['tools.ozone.set.defs#set'] = Field(
        default='tools.ozone.set.defs#set', alias='$type', frozen=True
    )


class SetView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.set.defs`."""

    created_at: str  #: Created at.
    name: str = Field(min_length=3, max_length=128)  #: Name.
    set_size: int  #: Set size.
    updated_at: str  #: Updated at.
    description: t.Optional[str] = Field(default=None, max_length=10240)  #: Description.

    py_type: t.Literal['tools.ozone.set.defs#setView'] = Field(
        default='tools.ozone.set.defs#setView', alias='$type', frozen=True
    )
