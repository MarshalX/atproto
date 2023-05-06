##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Type

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAppPassword`.

    Attributes:
        name: Name.
    """

    name: str


@dataclass
class AppPassword(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.createAppPassword`.

    Attributes:
        name: Name.
        password: Password.
        createdAt: Created at.
    """

    createdAt: str
    name: str
    password: str


#: Response reference to :obj:`AppPassword` model.
ResponseRef: Type[AppPassword] = AppPassword
