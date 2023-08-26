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

    """Input data model for :obj:`com.atproto.moderation.createReport`."""

    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.moderation.createReport`."""

    createdAt: str  #: Created at.
    id: int  #: Id.
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reportedBy: str  #: Reported by.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.
