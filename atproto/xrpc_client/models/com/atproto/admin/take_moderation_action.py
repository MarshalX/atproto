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
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.takeModerationAction`."""

    action: str  #: Action.
    createdBy: str  #: Created by.
    reason: str  #: Reason.
    subject: t.Union[
        'models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 't.Dict[str, t.Any]'
    ]  #: Subject.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    subjectBlobCids: t.Optional[t.List[str]] = None  #: Subject blob cids.


#: Response reference to :obj:`models.ComAtprotoAdminDefs.ActionView` model.
ResponseRef = models.ComAtprotoAdminDefs.ActionView
