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
    created_by: str = Field(alias='createdBy')  #: Created by.
    reason: str  #: Reason.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    create_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='createLabelVals')  #: Create label vals.
    duration_in_hours: t.Optional[int] = Field(
        default=None, alias='durationInHours'
    )  #: Indicates how long this action was meant to be in effect before automatically expiring.
    negate_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='negateLabelVals')  #: Negate label vals.
    subject_blob_cids: t.Optional[t.List[str]] = Field(default=None, alias='subjectBlobCids')  #: Subject blob cids.


class DataDict(te.TypedDict):
    action: str  #: Action.
    created_by: str  #: Created by.
    reason: str  #: Reason.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    create_label_vals: te.NotRequired[t.Optional[t.List[str]]]  #: Create label vals.
    duration_in_hours: te.NotRequired[
        t.Optional[int]
    ]  #: Indicates how long this action was meant to be in effect before automatically expiring.
    negate_label_vals: te.NotRequired[t.Optional[t.List[str]]]  #: Negate label vals.
    subject_blob_cids: te.NotRequired[t.Optional[t.List[str]]]  #: Subject blob cids.
