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

    """Input data model for :obj:`com.atproto.moderation.createReport`.

    Attributes:
        reasonType: Reason type.
        reason: Reason.
        subject: Subject.
    """

    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'
    subject: t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 't.Dict[str, t.Any]']
    reason: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.moderation.createReport`.

    Attributes:
        id: Id.
        reasonType: Reason type.
        reason: Reason.
        subject: Subject.
        reportedBy: Reported by.
        createdAt: Created at.
    """

    createdAt: str
    id: int
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'
    reportedBy: str
    subject: t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 't.Dict[str, t.Any]']
    reason: t.Optional[str] = None
