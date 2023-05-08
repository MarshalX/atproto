##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Literal

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class ActionView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        action: Action.
        subject: Subject.
        subjectBlobCids: Subject blob cids.
        createLabelVals: Create label vals.
        negateLabelVals: Negate label vals.
        reason: Reason.
        createdBy: Created by.
        createdAt: Created at.
        reversal: Reversal.
        resolvedReportIds: Resolved report ids.
    """

    action: 'models.ComAtprotoAdminDefs.ActionType'
    createdAt: str
    createdBy: str
    id: int
    reason: str
    resolvedReportIds: List[int]
    subject: Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 'Dict[str, Any]']
    subjectBlobCids: List[str]
    createLabelVals: Optional[List[str]] = None
    negateLabelVals: Optional[List[str]] = None
    reversal: Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None


@dataclass
class ActionViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        action: Action.
        subject: Subject.
        subjectBlobs: Subject blobs.
        createLabelVals: Create label vals.
        negateLabelVals: Negate label vals.
        reason: Reason.
        createdBy: Created by.
        createdAt: Created at.
        reversal: Reversal.
        resolvedReports: Resolved reports.
    """

    action: 'models.ComAtprotoAdminDefs.ActionType'
    createdAt: str
    createdBy: str
    id: int
    reason: str
    resolvedReports: List['models.ComAtprotoAdminDefs.ReportView']
    subject: Union['models.ComAtprotoAdminDefs.RepoView', 'models.ComAtprotoAdminDefs.RecordView', 'Dict[str, Any]']
    subjectBlobs: List['models.ComAtprotoAdminDefs.BlobView']
    createLabelVals: Optional[List[str]] = None
    negateLabelVals: Optional[List[str]] = None
    reversal: Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None


@dataclass
class ActionViewCurrent(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        action: Action.
    """

    action: 'models.ComAtprotoAdminDefs.ActionType'
    id: int


@dataclass
class ActionReversal(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        reason: Reason.
        createdBy: Created by.
        createdAt: Created at.
    """

    createdAt: str
    createdBy: str
    reason: str


ActionType = Literal['Takedown', 'Flag', 'Acknowledge', 'Escalate']

Takedown: Literal['takedown'] = 'takedown'

Flag: Literal['flag'] = 'flag'

Acknowledge: Literal['acknowledge'] = 'acknowledge'

Escalate: Literal['escalate'] = 'escalate'


@dataclass
class ReportView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        reasonType: Reason type.
        reason: Reason.
        subject: Subject.
        reportedBy: Reported by.
        createdAt: Created at.
        resolvedByActionIds: Resolved by action ids.
    """

    createdAt: str
    id: int
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'
    reportedBy: str
    resolvedByActionIds: List[int]
    subject: Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 'Dict[str, Any]']
    reason: Optional[str] = None


@dataclass
class ReportViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        reasonType: Reason type.
        reason: Reason.
        subject: Subject.
        reportedBy: Reported by.
        createdAt: Created at.
        resolvedByActions: Resolved by actions.
    """

    createdAt: str
    id: int
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'
    reportedBy: str
    resolvedByActions: List['models.ComAtprotoAdminDefs.ActionView']
    subject: Union['models.ComAtprotoAdminDefs.RepoView', 'models.ComAtprotoAdminDefs.RecordView', 'Dict[str, Any]']
    reason: Optional[str] = None


@dataclass
class RepoView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        did: Did.
        handle: Handle.
        email: Email.
        relatedRecords: Related records.
        indexedAt: Indexed at.
        moderation: Moderation.
        invitedBy: Invited by.
    """

    did: str
    handle: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.Moderation'
    relatedRecords: List['base.RecordModelBase']
    email: Optional[str] = None
    invitedBy: Optional['models.ComAtprotoServerDefs.InviteCode'] = None


@dataclass
class RepoViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        did: Did.
        handle: Handle.
        email: Email.
        relatedRecords: Related records.
        indexedAt: Indexed at.
        moderation: Moderation.
        labels: Labels.
        invitedBy: Invited by.
        invites: Invites.
    """

    did: str
    handle: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'
    relatedRecords: List['base.RecordModelBase']
    email: Optional[str] = None
    invitedBy: Optional['models.ComAtprotoServerDefs.InviteCode'] = None
    invites: Optional[List['models.ComAtprotoServerDefs.InviteCode']] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None


@dataclass
class RepoRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        did: Did.
    """

    did: str


@dataclass
class RecordView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        uri: Uri.
        cid: Cid.
        value: Value.
        blobCids: Blob cids.
        indexedAt: Indexed at.
        moderation: Moderation.
        repo: Repo.
    """

    blobCids: List[str]
    cid: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.Moderation'
    repo: 'models.ComAtprotoAdminDefs.RepoView'
    uri: str
    value: 'base.RecordModelBase'


@dataclass
class RecordViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        uri: Uri.
        cid: Cid.
        value: Value.
        blobs: Blobs.
        labels: Labels.
        indexedAt: Indexed at.
        moderation: Moderation.
        repo: Repo.
    """

    blobs: List['models.ComAtprotoAdminDefs.BlobView']
    cid: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'
    repo: 'models.ComAtprotoAdminDefs.RepoView'
    uri: str
    value: 'base.RecordModelBase'
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None


@dataclass
class Moderation(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        currentAction: Current action.
    """

    currentAction: Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None


@dataclass
class ModerationDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        currentAction: Current action.
        actions: Actions.
        reports: Reports.
    """

    actions: List['models.ComAtprotoAdminDefs.ActionView']
    reports: List['models.ComAtprotoAdminDefs.ReportView']
    currentAction: Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None


@dataclass
class BlobView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        cid: Cid.
        mimeType: Mime type.
        size: Size.
        createdAt: Created at.
        details: Details.
        moderation: Moderation.
    """

    cid: str
    createdAt: str
    mimeType: str
    size: int
    details: Optional[
        Union['models.ComAtprotoAdminDefs.ImageDetails', 'models.ComAtprotoAdminDefs.VideoDetails', 'Dict[str, Any]']
    ] = None
    moderation: Optional['models.ComAtprotoAdminDefs.Moderation'] = None


@dataclass
class ImageDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        width: Width.
        height: Height.
    """

    height: int
    width: int


@dataclass
class VideoDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        width: Width.
        height: Height.
        length: Length.
    """

    height: int
    length: int
    width: int
