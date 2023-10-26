##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.reverseModerationAction`."""

    created_by: str = Field(alias='createdBy')  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.


class DataDict(te.TypedDict):
    created_by: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
