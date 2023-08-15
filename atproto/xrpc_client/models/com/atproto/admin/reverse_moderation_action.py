##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.reverseModerationAction`."""

    createdBy: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.


#: Response reference to :obj:`models.ComAtprotoAdminDefs.ActionView` model.
ResponseRef = 'models.ComAtprotoAdminDefs.ActionView'
