##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.admin.takeModerationAction`."""

    action: str  #: Action.
    createdBy: str  #: Created by.
    reason: str  #: Reason.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    durationInHours: t.Optional[
        int
    ] = None  #: Indicates how long this action was meant to be in effect before automatically expiring.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    subjectBlobCids: t.Optional[t.List[str]] = None  #: Subject blob cids.
