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
from atproto.xrpc_client.models import base, unknown_type


class ActionView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolvedReportIds: t.List[int]  #: Resolved report ids.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subjectBlobCids: t.List[str]  #: Subject blob cids.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    py_type: te.Literal['com.atproto.admin.defs#actionView'] = Field(
        default='com.atproto.admin.defs#actionView', alias='$type'
    )


class ActionViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolvedReports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Resolved reports.
    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoView',
            'models.ComAtprotoAdminDefs.RepoViewNotFound',
            'models.ComAtprotoAdminDefs.RecordView',
            'models.ComAtprotoAdminDefs.RecordViewNotFound',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subjectBlobs: t.List['models.ComAtprotoAdminDefs.BlobView']  #: Subject blobs.
    createLabelVals: t.Optional[t.List[str]] = None  #: Create label vals.
    negateLabelVals: t.Optional[t.List[str]] = None  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    py_type: te.Literal['com.atproto.admin.defs#actionViewDetail'] = Field(
        default='com.atproto.admin.defs#actionViewDetail', alias='$type'
    )


class ActionViewCurrent(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    id: int  #: Id.

    py_type: te.Literal['com.atproto.admin.defs#actionViewCurrent'] = Field(
        default='com.atproto.admin.defs#actionViewCurrent', alias='$type'
    )


class ActionReversal(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    createdBy: str  #: Created by.
    reason: str  #: Reason.

    py_type: te.Literal['com.atproto.admin.defs#actionReversal'] = Field(
        default='com.atproto.admin.defs#actionReversal', alias='$type'
    )


ActionType = t.Union[
    'models.ComAtprotoAdminDefs.Takedown',
    'models.ComAtprotoAdminDefs.Flag',
    'models.ComAtprotoAdminDefs.Acknowledge',
    'models.ComAtprotoAdminDefs.Escalate',
]  #: Action type

Takedown = te.Literal[
    'com.atproto.admin.defs#takedown'
]  #: Moderation action type: Takedown. Indicates that content should not be served by the PDS.

Flag = te.Literal[
    'com.atproto.admin.defs#flag'
]  #: Moderation action type: Flag. Indicates that the content was reviewed and considered to violate PDS rules, but may still be served.

Acknowledge = te.Literal[
    'com.atproto.admin.defs#acknowledge'
]  #: Moderation action type: Acknowledge. Indicates that the content was reviewed and not considered to violate PDS rules.

Escalate = te.Literal[
    'com.atproto.admin.defs#escalate'
]  #: Moderation action type: Escalate. Indicates that the content has been flagged for additional review.


class ReportView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    id: int  #: Id.
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reportedBy: str  #: Reported by.
    resolvedByActionIds: t.List[int]  #: Resolved by action ids.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.
    subjectRepoHandle: t.Optional[str] = None  #: Subject repo handle.

    py_type: te.Literal['com.atproto.admin.defs#reportView'] = Field(
        default='com.atproto.admin.defs#reportView', alias='$type'
    )


class ReportViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    createdAt: str  #: Created at.
    id: int  #: Id.
    reasonType: 'models.ComAtprotoModerationDefs.ReasonType'  #: Reason type.
    reportedBy: str  #: Reported by.
    resolvedByActions: t.List['models.ComAtprotoAdminDefs.ActionView']  #: Resolved by actions.
    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoView',
            'models.ComAtprotoAdminDefs.RepoViewNotFound',
            'models.ComAtprotoAdminDefs.RecordView',
            'models.ComAtprotoAdminDefs.RecordViewNotFound',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.

    py_type: te.Literal['com.atproto.admin.defs#reportViewDetail'] = Field(
        default='com.atproto.admin.defs#reportViewDetail', alias='$type'
    )


class RepoView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    relatedRecords: t.List['unknown_type.UnknownType']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    inviteNote: t.Optional[str] = None  #: Invite note.
    invitedBy: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invitesDisabled: t.Optional[bool] = None  #: Invites disabled.

    py_type: te.Literal['com.atproto.admin.defs#repoView'] = Field(
        default='com.atproto.admin.defs#repoView', alias='$type'
    )


class RepoViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    relatedRecords: t.List['unknown_type.UnknownType']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    inviteNote: t.Optional[str] = None  #: Invite note.
    invitedBy: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invitesDisabled: t.Optional[bool] = None  #: Invites disabled.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['com.atproto.admin.defs#repoViewDetail'] = Field(
        default='com.atproto.admin.defs#repoViewDetail', alias='$type'
    )


class RepoViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    py_type: te.Literal['com.atproto.admin.defs#repoViewNotFound'] = Field(
        default='com.atproto.admin.defs#repoViewNotFound', alias='$type'
    )


class RepoRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    py_type: te.Literal['com.atproto.admin.defs#repoRef'] = Field(
        default='com.atproto.admin.defs#repoRef', alias='$type'
    )


class RecordView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blobCids: t.List[str]  #: Blob cids.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'unknown_type.UnknownType'  #: Value.

    py_type: te.Literal['com.atproto.admin.defs#recordView'] = Field(
        default='com.atproto.admin.defs#recordView', alias='$type'
    )


class RecordViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blobs: t.List['models.ComAtprotoAdminDefs.BlobView']  #: Blobs.
    cid: str  #: Cid.
    indexedAt: str  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'unknown_type.UnknownType'  #: Value.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['com.atproto.admin.defs#recordViewDetail'] = Field(
        default='com.atproto.admin.defs#recordViewDetail', alias='$type'
    )


class RecordViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    uri: str  #: Uri.

    py_type: te.Literal['com.atproto.admin.defs#recordViewNotFound'] = Field(
        default='com.atproto.admin.defs#recordViewNotFound', alias='$type'
    )


class Moderation(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    currentAction: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None  #: Current action.

    py_type: te.Literal['com.atproto.admin.defs#moderation'] = Field(
        default='com.atproto.admin.defs#moderation', alias='$type'
    )


class ModerationDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    actions: t.List['models.ComAtprotoAdminDefs.ActionView']  #: Actions.
    reports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Reports.
    currentAction: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = None  #: Current action.

    py_type: te.Literal['com.atproto.admin.defs#moderationDetail'] = Field(
        default='com.atproto.admin.defs#moderationDetail', alias='$type'
    )


class BlobView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    cid: str  #: Cid.
    createdAt: str  #: Created at.
    mimeType: str  #: Mime type.
    size: int  #: Size.
    details: t.Optional[
        te.Annotated[
            t.Union['models.ComAtprotoAdminDefs.ImageDetails', 'models.ComAtprotoAdminDefs.VideoDetails'],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Details.
    moderation: t.Optional['models.ComAtprotoAdminDefs.Moderation'] = None  #: Moderation.

    py_type: te.Literal['com.atproto.admin.defs#blobView'] = Field(
        default='com.atproto.admin.defs#blobView', alias='$type'
    )


class ImageDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    width: int  #: Width.

    py_type: te.Literal['com.atproto.admin.defs#imageDetails'] = Field(
        default='com.atproto.admin.defs#imageDetails', alias='$type'
    )


class VideoDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    length: int  #: Length.
    width: int  #: Width.

    py_type: te.Literal['com.atproto.admin.defs#videoDetails'] = Field(
        default='com.atproto.admin.defs#videoDetails', alias='$type'
    )
