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
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class StatusAttr(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    applied: bool  #: Applied.
    ref: t.Optional[str] = None  #: Ref.

    py_type: te.Literal['com.atproto.admin.defs#statusAttr'] = Field(
        default='com.atproto.admin.defs#statusAttr', alias='$type', frozen=True
    )


class ActionView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    created_at: str = Field(alias='createdAt')  #: Created at.
    created_by: str = Field(alias='createdBy')  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolved_report_ids: t.List[int] = Field(alias='resolvedReportIds')  #: Resolved report ids.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: t.List[str] = Field(alias='subjectBlobCids')  #: Subject blob cids.
    create_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='createLabelVals')  #: Create label vals.
    duration_in_hours: t.Optional[int] = Field(
        default=None, alias='durationInHours'
    )  #: Indicates how long this action was meant to be in effect before automatically expiring.
    negate_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='negateLabelVals')  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    py_type: te.Literal['com.atproto.admin.defs#actionView'] = Field(
        default='com.atproto.admin.defs#actionView', alias='$type', frozen=True
    )


class ActionViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    created_at: str = Field(alias='createdAt')  #: Created at.
    created_by: str = Field(alias='createdBy')  #: Created by.
    id: int  #: Id.
    reason: str  #: Reason.
    resolved_reports: t.List['models.ComAtprotoAdminDefs.ReportView'] = Field(
        alias='resolvedReports'
    )  #: Resolved reports.
    subject: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.RepoView',
            'models.ComAtprotoAdminDefs.RepoViewNotFound',
            'models.ComAtprotoAdminDefs.RecordView',
            'models.ComAtprotoAdminDefs.RecordViewNotFound',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blobs: t.List['models.ComAtprotoAdminDefs.BlobView'] = Field(alias='subjectBlobs')  #: Subject blobs.
    create_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='createLabelVals')  #: Create label vals.
    duration_in_hours: t.Optional[int] = Field(
        default=None, alias='durationInHours'
    )  #: Indicates how long this action was meant to be in effect before automatically expiring.
    negate_label_vals: t.Optional[t.List[str]] = Field(default=None, alias='negateLabelVals')  #: Negate label vals.
    reversal: t.Optional['models.ComAtprotoAdminDefs.ActionReversal'] = None  #: Reversal.

    py_type: te.Literal['com.atproto.admin.defs#actionViewDetail'] = Field(
        default='com.atproto.admin.defs#actionViewDetail', alias='$type', frozen=True
    )


class ActionViewCurrent(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    action: 'models.ComAtprotoAdminDefs.ActionType'  #: Action.
    id: int  #: Id.
    duration_in_hours: t.Optional[int] = Field(
        default=None, alias='durationInHours'
    )  #: Indicates how long this action was meant to be in effect before automatically expiring.

    py_type: te.Literal['com.atproto.admin.defs#actionViewCurrent'] = Field(
        default='com.atproto.admin.defs#actionViewCurrent', alias='$type', frozen=True
    )


class ActionReversal(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    created_by: str = Field(alias='createdBy')  #: Created by.
    reason: str  #: Reason.

    py_type: te.Literal['com.atproto.admin.defs#actionReversal'] = Field(
        default='com.atproto.admin.defs#actionReversal', alias='$type', frozen=True
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

    created_at: str = Field(alias='createdAt')  #: Created at.
    id: int  #: Id.
    reason_type: 'models.ComAtprotoModerationDefs.ReasonType' = Field(alias='reasonType')  #: Reason type.
    reported_by: str = Field(alias='reportedBy')  #: Reported by.
    resolved_by_action_ids: t.List[int] = Field(alias='resolvedByActionIds')  #: Resolved by action ids.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    reason: t.Optional[str] = None  #: Reason.
    subject_repo_handle: t.Optional[str] = Field(default=None, alias='subjectRepoHandle')  #: Subject repo handle.

    py_type: te.Literal['com.atproto.admin.defs#reportView'] = Field(
        default='com.atproto.admin.defs#reportView', alias='$type', frozen=True
    )


class ReportViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    id: int  #: Id.
    reason_type: 'models.ComAtprotoModerationDefs.ReasonType' = Field(alias='reasonType')  #: Reason type.
    reported_by: str = Field(alias='reportedBy')  #: Reported by.
    resolved_by_actions: t.List['models.ComAtprotoAdminDefs.ActionView'] = Field(
        alias='resolvedByActions'
    )  #: Resolved by actions.
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
        default='com.atproto.admin.defs#reportViewDetail', alias='$type', frozen=True
    )


class RepoView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    related_records: t.List['UnknownType'] = Field(alias='relatedRecords')  #: Related records.
    email: t.Optional[str] = None  #: Email.
    invite_note: t.Optional[str] = Field(default=None, alias='inviteNote')  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = Field(
        default=None, alias='invitedBy'
    )  #: Invited by.
    invites_disabled: t.Optional[bool] = Field(default=None, alias='invitesDisabled')  #: Invites disabled.

    py_type: te.Literal['com.atproto.admin.defs#repoView'] = Field(
        default='com.atproto.admin.defs#repoView', alias='$type', frozen=True
    )


class RepoViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    related_records: t.List['UnknownType'] = Field(alias='relatedRecords')  #: Related records.
    email: t.Optional[str] = None  #: Email.
    invite_note: t.Optional[str] = Field(default=None, alias='inviteNote')  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = Field(
        default=None, alias='invitedBy'
    )  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invites_disabled: t.Optional[bool] = Field(default=None, alias='invitesDisabled')  #: Invites disabled.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['com.atproto.admin.defs#repoViewDetail'] = Field(
        default='com.atproto.admin.defs#repoViewDetail', alias='$type', frozen=True
    )


class AccountView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    email: t.Optional[str] = None  #: Email.
    invite_note: t.Optional[str] = Field(default=None, alias='inviteNote')  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = Field(
        default=None, alias='invitedBy'
    )  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invites_disabled: t.Optional[bool] = Field(default=None, alias='invitesDisabled')  #: Invites disabled.

    py_type: te.Literal['com.atproto.admin.defs#accountView'] = Field(
        default='com.atproto.admin.defs#accountView', alias='$type', frozen=True
    )


class RepoViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    py_type: te.Literal['com.atproto.admin.defs#repoViewNotFound'] = Field(
        default='com.atproto.admin.defs#repoViewNotFound', alias='$type', frozen=True
    )


class RepoRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    did: str  #: Did.

    py_type: te.Literal['com.atproto.admin.defs#repoRef'] = Field(
        default='com.atproto.admin.defs#repoRef', alias='$type', frozen=True
    )


class RepoBlobRef(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    cid: str  #: Cid.
    did: str  #: Did.
    record_uri: t.Optional[str] = Field(default=None, alias='recordUri')  #: Record uri.

    py_type: te.Literal['com.atproto.admin.defs#repoBlobRef'] = Field(
        default='com.atproto.admin.defs#repoBlobRef', alias='$type', frozen=True
    )


class RecordView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blob_cids: t.List[str] = Field(alias='blobCids')  #: Blob cids.
    cid: str  #: Cid.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.Moderation'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'UnknownType'  #: Value.

    py_type: te.Literal['com.atproto.admin.defs#recordView'] = Field(
        default='com.atproto.admin.defs#recordView', alias='$type', frozen=True
    )


class RecordViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    blobs: t.List['models.ComAtprotoAdminDefs.BlobView']  #: Blobs.
    cid: str  #: Cid.
    indexed_at: str = Field(alias='indexedAt')  #: Indexed at.
    moderation: 'models.ComAtprotoAdminDefs.ModerationDetail'  #: Moderation.
    repo: 'models.ComAtprotoAdminDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'UnknownType'  #: Value.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['com.atproto.admin.defs#recordViewDetail'] = Field(
        default='com.atproto.admin.defs#recordViewDetail', alias='$type', frozen=True
    )


class RecordViewNotFound(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    uri: str  #: Uri.

    py_type: te.Literal['com.atproto.admin.defs#recordViewNotFound'] = Field(
        default='com.atproto.admin.defs#recordViewNotFound', alias='$type', frozen=True
    )


class Moderation(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    current_action: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = Field(
        default=None, alias='currentAction'
    )  #: Current action.

    py_type: te.Literal['com.atproto.admin.defs#moderation'] = Field(
        default='com.atproto.admin.defs#moderation', alias='$type', frozen=True
    )


class ModerationDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    actions: t.List['models.ComAtprotoAdminDefs.ActionView']  #: Actions.
    reports: t.List['models.ComAtprotoAdminDefs.ReportView']  #: Reports.
    current_action: t.Optional['models.ComAtprotoAdminDefs.ActionViewCurrent'] = Field(
        default=None, alias='currentAction'
    )  #: Current action.

    py_type: te.Literal['com.atproto.admin.defs#moderationDetail'] = Field(
        default='com.atproto.admin.defs#moderationDetail', alias='$type', frozen=True
    )


class BlobView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    cid: str  #: Cid.
    created_at: str = Field(alias='createdAt')  #: Created at.
    mime_type: str = Field(alias='mimeType')  #: Mime type.
    size: int  #: Size.
    details: t.Optional[
        te.Annotated[
            t.Union['models.ComAtprotoAdminDefs.ImageDetails', 'models.ComAtprotoAdminDefs.VideoDetails'],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Details.
    moderation: t.Optional['models.ComAtprotoAdminDefs.Moderation'] = None  #: Moderation.

    py_type: te.Literal['com.atproto.admin.defs#blobView'] = Field(
        default='com.atproto.admin.defs#blobView', alias='$type', frozen=True
    )


class ImageDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    width: int  #: Width.

    py_type: te.Literal['com.atproto.admin.defs#imageDetails'] = Field(
        default='com.atproto.admin.defs#imageDetails', alias='$type', frozen=True
    )


class VideoDetails(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    height: int  #: Height.
    length: int  #: Length.
    width: int  #: Width.

    py_type: te.Literal['com.atproto.admin.defs#videoDetails'] = Field(
        default='com.atproto.admin.defs#videoDetails', alias='$type', frozen=True
    )
