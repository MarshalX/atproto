##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.server.createAppPassword`."""

    name: str  #: Name.


@dataclass
class AppPassword(base.ModelBase):

    """Definition model for :obj:`com.atproto.server.createAppPassword`."""

    createdAt: str  #: Created at.
    name: str  #: Name.
    password: str  #: Password.

    _type: str = 'com.atproto.server.createAppPassword#appPassword'


#: Response reference to :obj:`AppPassword` model.
ResponseRef = AppPassword
