##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.takeModerationAction`.

    Attributes:
        action: Action.
        subject: Subject.
        subjectBlobCids: Subject blob cids.
        createLabelVals: Create label vals.
        negateLabelVals: Negate label vals.
        reason: Reason.
        createdBy: Created by.
    """

    action: str
    createdBy: str
    reason: str
    subject: Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 'Dict[str, Any]']
    createLabelVals: Optional[List[str]] = None
    negateLabelVals: Optional[List[str]] = None
    subjectBlobCids: Optional[List[str]] = None


#: Response reference to :obj:`models.ComAtprotoAdminDefs.ActionView` model.
ResponseRef: Type[models.ComAtprotoAdminDefs.ActionView] = models.ComAtprotoAdminDefs.ActionView
