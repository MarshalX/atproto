##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.server.createAppPassword`."""

    name: str  #: A short name for the App Password, to help distinguish them.


class DataDict(t.TypedDict):
    name: str  #: A short name for the App Password, to help distinguish them.


class AppPassword(base.ModelBase):
    """Definition model for :obj:`com.atproto.server.createAppPassword`."""

    created_at: str  #: Created at.
    name: str  #: Name.
    password: str  #: Password.

    py_type: t.Literal['com.atproto.server.createAppPassword#appPassword'] = Field(
        default='com.atproto.server.createAppPassword#appPassword', alias='$type', frozen=True
    )
