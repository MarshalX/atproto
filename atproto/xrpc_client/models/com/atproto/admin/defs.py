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

    _type: str = 'com.atproto.admin.defs#actionView'


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
    subject: Union[
        'models.ComAtprotoAdminDefs.RepoView',
        'models.ComAtprotoAdminDefs.RepoViewNotFound',
        'models.ComAtprotoAdminDefs.RecordView',
        'models.ComAtprotoAdminDefs.RecordViewNotFound',
        'Dict[str, Any]',
    ]
    subjectBlobs: List['models.ComAtprotoAdminDefs.BlobView']
    createLabelVals: Optional[List[str]] = None
    negateLabelVals: Optional[List[str]] = None
    reversal: Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None

    _type: str = 'com.atproto.admin.defs#actionViewDetail'


@dataclass
class ActionViewCurrent(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        id: Id.
        action: Action.
    """

    action: 'models.ComAtprotoAdminDefs.ActionType'
    id: int

    _type: str = 'com.atproto.admin.defs#actionViewCurrent'


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

    _type: str = 'com.atproto.admin.defs#actionReversal'


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

    _type: str = 'com.atproto.admin.defs#reportView'


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
    subject: Union[
        'models.ComAtprotoAdminDefs.RepoView',
        'models.ComAtprotoAdminDefs.RepoViewNotFound',
        'models.ComAtprotoAdminDefs.RecordView',
        'models.ComAtprotoAdminDefs.RecordViewNotFound',
        'Dict[str, Any]',
    ]
    reason: Optional[str] = None

    _type: str = 'com.atproto.admin.defs#reportViewDetail'


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
        invitesDisabled: Invites disabled.
    """

    did: str
    handle: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.Moderation'
    relatedRecords: List['base.RecordModelBase']
    email: Optional[str] = None
    invitedBy: Optional['models.ComAtprotoServerDefs.InviteCode'] = None
    invitesDisabled: Optional[bool] = None

    _type: str = 'com.atproto.admin.defs#repoView'


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
        invitesDisabled: Invites disabled.
    """

    did: str
    handle: str
    indexedAt: str
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'
    relatedRecords: List['base.RecordModelBase']
    email: Optional[str] = None
    invitedBy: Optional['models.ComAtprotoServerDefs.InviteCode'] = None
    invites: Optional[List['models.ComAtprotoServerDefs.InviteCode']] = None
    invitesDisabled: Optional[bool] = None
    labels: Optional[List['models.ComAtprotoLabelDefs.Label']] = None

    _type: str = 'com.atproto.admin.defs#repoViewDetail'


@dataclass
class RepoViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        did: Did.
    """

    did: str

    _type: str = 'com.atproto.admin.defs#repoViewNotFound'


@dataclass
class RepoRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        did: Did.
    """

    did: str

    _type: str = 'com.atproto.admin.defs#repoRef'


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

    _type: str = 'com.atproto.admin.defs#recordView'


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

    _type: str = 'com.atproto.admin.defs#recordViewDetail'


@dataclass
class RecordViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        uri: Uri.
    """

    uri: str

    _type: str = 'com.atproto.admin.defs#recordViewNotFound'


@dataclass
class Moderation(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        currentAction: Current action.
    """

    currentAction: Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None

    _type: str = 'com.atproto.admin.defs#moderation'


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

    _type: str = 'com.atproto.admin.defs#moderationDetail'


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

    _type: str = 'com.atproto.admin.defs#blobView'


@dataclass
class ImageDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`.

    Attributes:
        width: Width.
        height: Height.
    """

    height: int
    width: int

    _type: str = 'com.atproto.admin.defs#imageDetails'


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

    _type: str = 'com.atproto.admin.defs#videoDetails'
