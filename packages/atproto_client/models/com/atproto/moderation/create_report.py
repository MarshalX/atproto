##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.moderation.createReport`."""

    reason_type: (
        'models.ComAtprotoModerationDefs.ReasonType'
    )  #: Indicates the broad category of violation the report is for.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Additional context about the content and violation.


class DataDict(te.TypedDict):
    reason_type: (
        'models.ComAtprotoModerationDefs.ReasonType'
    )  #: Indicates the broad category of violation the report is for.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: te.NotRequired[t.Optional[str]]  #: Additional context about the content and violation.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.moderation.createReport`."""

    created_at: str  #: Created at.
    id: int  #: Id.
    reason_type: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reported_by: str  #: Reported by.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = Field(default=None, max_length=20000)  #: Reason.
