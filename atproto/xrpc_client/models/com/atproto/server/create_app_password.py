##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAppPassword`."""

    name: str  #: Name.


class DataDict(te.TypedDict):
    name: str  #: Name.


class AppPassword(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.createAppPassword`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    name: str  #: Name.
    password: str  #: Password.

    py_type: te.Literal['com.atproto.server.createAppPassword#appPassword'] = Field(
        default='com.atproto.server.createAppPassword#appPassword', alias='$type', frozen=True
    )
