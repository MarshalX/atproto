##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class ActionView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolvedReportIds: t.List[int]  #: Resolved report ids.
    subject: t.Union[
        'models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 't.Dict[str, t.Any]'
    ]  #: Subject.
    subjectBlobCids: t.List[str]  #: Subject blob cids.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    _type: str = 'com.atproto.admin.defs#actionView'


class ActionViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolvedReports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Resolved reports.
    subject: t.Union[
        'models.ComAtprotoAdminDefs.RepoView',
        'models.ComAtprotoAdminDefs.RepoViewNotFound',
        'models.ComAtprotoAdminDefs.RecordView',
        'models.ComAtprotoAdminDefs.RecordViewNotFound',
        't.Dict[str, t.Any]',
    ]  #: Subject.
    subjectBlobs: t.List['models.ComAtprotoAdminDefs.BlobView']  #: Subject blobs.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    _type: str = 'com.atproto.admin.defs#actionViewDetail'


class ActionViewCurrent(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    id: int  #: Id.

    _type: str = 'com.atproto.admin.defs#actionViewCurrent'


class ActionReversal(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    reason: str  #: Reason.

    _type: str = 'com.atproto.admin.defs#actionReversal'


ActionType = te.Literal['Takedown', 'Flag', 'Acknowledge', 'Escalate']

Takedown: te.Literal['takedown'] = 'takedown'

Flag: te.Literal['flag'] = 'flag'

Acknowledge: te.Literal['acknowledge'] = 'acknowledge'

Escalate: te.Literal['escalate'] = 'escalate'


class ReportView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    id: int  #: Id.
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reportedBy: str  #: Reported by.
    resolvedByActionIds: t.List[int]  #: Resolved by action ids.
    subject: t.Union[
        'models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main', 't.Dict[str, t.Any]'
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.
    subjectRepoHandle: t.Optional[str] = None  #: Subject repo handle.

    _type: str = 'com.atproto.admin.defs#reportView'


class ReportViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    id: int  #: Id.
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reportedBy: str  #: Reported by.
    resolvedByActions: t.List['models.ComAtprotoAdminDefs.ActionView']  #: Resolved by actions.
    subject: t.Union[
        'models.ComAtprotoAdminDefs.RepoView',
        'models.ComAtprotoAdminDefs.RepoViewNotFound',
        'models.ComAtprotoAdminDefs.RecordView',
        'models.ComAtprotoAdminDefs.RecordViewNotFound',
        't.Dict[str, t.Any]',
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.

    _type: str = 'com.atproto.admin.defs#reportViewDetail'


class RepoView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    relatedRecords: t.List['base.UnknownDict']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    inviteNote: t.Optional[str] = None  #: Invite note.
    invitedBy: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invitesDisabled: t.Optional[bool] = None  #: Invites disabled.

    _type: str = 'com.atproto.admin.defs#repoView'


class RepoViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    relatedRecords: t.List['base.UnknownDict']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    inviteNote: t.Optional[str] = None  #: Invite note.
    invitedBy: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invitesDisabled: t.Optional[bool] = None  #: Invites disabled.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    _type: str = 'com.atproto.admin.defs#repoViewDetail'


class RepoViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    _type: str = 'com.atproto.admin.defs#repoViewNotFound'


class RepoRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    _type: str = 'com.atproto.admin.defs#repoRef'


class RecordView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blobCids: t.List[str]  #: Blob cids.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'base.UnknownDict'  #: Value.

    _type: str = 'com.atproto.admin.defs#recordView'


class RecordViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blobs: t.List['models.ComAtprotoAdminDefs.BlobView']  #: Blobs.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'base.UnknownDict'  #: Value.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    _type: str = 'com.atproto.admin.defs#recordViewDetail'


class RecordViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    uri: str  #: Uri.

    _type: str = 'com.atproto.admin.defs#recordViewNotFound'


class Moderation(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    currentAction: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None  #: Current action.

    _type: str = 'com.atproto.admin.defs#moderation'


class ModerationDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    actions: t.List['models.ComAtprotoAdminDefs.ActionView']  #: Actions.
    reports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Reports.
    currentAction: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None  #: Current action.

    _type: str = 'com.atproto.admin.defs#moderationDetail'


class BlobView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    cid: str  #: Cid.
    createdAt: str  #: Created at.
    mimeType: str  #: Mime type.
    size: int  #: Size.
    details: t.Optional[
        t.Union[
            'models.ComAtprotoAdminDefs.ImageDetails', 'models.ComAtprotoAdminDefs.VideoDetails', 't.Dict[str, t.Any]'
        ]
    ] = None  #: Details.
    moderation: t.Optional['models.ComAtprotoAdminDefs.Moderation'] = None  #: Moderation.

    _type: str = 'com.atproto.admin.defs#blobView'


class ImageDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    width: int  #: Width.

    _type: str = 'com.atproto.admin.defs#imageDetails'


class VideoDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    length: int  #: Length.
    width: int  #: Width.

    _type: str = 'com.atproto.admin.defs#videoDetails'
