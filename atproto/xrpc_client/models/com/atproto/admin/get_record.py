##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.getRecord`."""

    uri: str  #: Uri.
    cid: t.Optional[str] = None  #: Cid.


#: Response reference to :obj:`models.ComAtprotoAdminDefs.RecordViewDetail` model.
ResponseRef: t.Type[models.ComAtprotoAdminDefs.RecordViewDetail] = models.ComAtprotoAdminDefs.RecordViewDetail
