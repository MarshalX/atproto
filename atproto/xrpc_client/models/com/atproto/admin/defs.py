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


class ModEventView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    created_by: str = Field(alias='createdBy')  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.ModEventTakedown',
            'models.ComAtprotoAdminDefs.ModEventReverseTakedown',
            'models.ComAtprotoAdminDefs.ModEventComment',
            'models.ComAtprotoAdminDefs.ModEventReport',
            'models.ComAtprotoAdminDefs.ModEventLabel',
            'models.ComAtprotoAdminDefs.ModEventAcknowledge',
            'models.ComAtprotoAdminDefs.ModEventEscalate',
            'models.ComAtprotoAdminDefs.ModEventMute',
            'models.ComAtprotoAdminDefs.ModEventEmail',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    id: int  #: Id.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: t.List[str] = Field(alias='subjectBlobCids')  #: Subject blob cids.
    creator_handle: t.Optional[str] = Field(default=None, alias='creatorHandle')  #: Creator handle.
    subject_handle: t.Optional[str] = Field(default=None, alias='subjectHandle')  #: Subject handle.

    py_type: te.Literal['com.atproto.admin.defs#modEventView'] = Field(
        default='com.atproto.admin.defs#modEventView', alias='$type', frozen=True
    )


class ModEventViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    created_by: str = Field(alias='createdBy')  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ComAtprotoAdminDefs.ModEventTakedown',
            'models.ComAtprotoAdminDefs.ModEventReverseTakedown',
            'models.ComAtprotoAdminDefs.ModEventComment',
            'models.ComAtprotoAdminDefs.ModEventReport',
            'models.ComAtprotoAdminDefs.ModEventLabel',
            'models.ComAtprotoAdminDefs.ModEventAcknowledge',
            'models.ComAtprotoAdminDefs.ModEventEscalate',
            'models.ComAtprotoAdminDefs.ModEventMute',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    id: int  #: Id.
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

    py_type: te.Literal['com.atproto.admin.defs#modEventViewDetail'] = Field(
        default='com.atproto.admin.defs#modEventViewDetail', alias='$type', frozen=True
    )


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
    comment: t.Optional[str] = None  #: Comment.
    subject_repo_handle: t.Optional[str] = Field(default=None, alias='subjectRepoHandle')  #: Subject repo handle.

    py_type: te.Literal['com.atproto.admin.defs#reportView'] = Field(
        default='com.atproto.admin.defs#reportView', alias='$type', frozen=True
    )


class SubjectStatusView(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(
        alias='createdAt'
    )  #: Timestamp referencing the first moderation status impacting event was emitted on the subject.
    id: int  #: Id.
    review_state: 'models.ComAtprotoAdminDefs.SubjectReviewState' = Field(alias='reviewState')  #: Review state.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    updated_at: str = Field(
        alias='updatedAt'
    )  #: Timestamp referencing when the last update was made to the moderation status of the subject.
    comment: t.Optional[str] = None  #: Sticky comment on the subject.
    last_reported_at: t.Optional[str] = Field(default=None, alias='lastReportedAt')  #: Last reported at.
    last_reviewed_at: t.Optional[str] = Field(default=None, alias='lastReviewedAt')  #: Last reviewed at.
    last_reviewed_by: t.Optional[str] = Field(default=None, alias='lastReviewedBy')  #: Last reviewed by.
    mute_until: t.Optional[str] = Field(default=None, alias='muteUntil')  #: Mute until.
    subject_blob_cids: t.Optional[t.List[str]] = Field(default=None, alias='subjectBlobCids')  #: Subject blob cids.
    subject_repo_handle: t.Optional[str] = Field(default=None, alias='subjectRepoHandle')  #: Subject repo handle.
    suspend_until: t.Optional[str] = Field(default=None, alias='suspendUntil')  #: Suspend until.
    takendown: t.Optional[bool] = None  #: Takendown.

    py_type: te.Literal['com.atproto.admin.defs#subjectStatusView'] = Field(
        default='com.atproto.admin.defs#subjectStatusView', alias='$type', frozen=True
    )


class ReportViewDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    id: int  #: Id.
    reason_type: 'models.ComAtprotoModerationDefs.ReasonType' = Field(alias='reasonType')  #: Reason type.
    reported_by: str = Field(alias='reportedBy')  #: Reported by.
    resolved_by_actions: t.List['models.ComAtprotoAdminDefs.ModEventView'] = Field(
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
    comment: t.Optional[str] = None  #: Comment.
    subject_status: t.Optional['models.ComAtprotoAdminDefs.SubjectStatusView'] = Field(
        default=None, alias='subjectStatus'
    )  #: Subject status.

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
    email_confirmed_at: t.Optional[str] = Field(default=None, alias='emailConfirmedAt')  #: Email confirmed at.
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
    email_confirmed_at: t.Optional[str] = Field(default=None, alias='emailConfirmedAt')  #: Email confirmed at.
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

    subject_status: t.Optional['models.ComAtprotoAdminDefs.SubjectStatusView'] = Field(
        default=None, alias='subjectStatus'
    )  #: Subject status.

    py_type: te.Literal['com.atproto.admin.defs#moderation'] = Field(
        default='com.atproto.admin.defs#moderation', alias='$type', frozen=True
    )


class ModerationDetail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    subject_status: t.Optional['models.ComAtprotoAdminDefs.SubjectStatusView'] = Field(
        default=None, alias='subjectStatus'
    )  #: Subject status.

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


SubjectReviewState = t.Union[
    'models.ComAtprotoAdminDefs.ReviewOpen',
    'models.ComAtprotoAdminDefs.ReviewEscalated',
    'models.ComAtprotoAdminDefs.ReviewClosed',
]  #: Subject review state

ReviewOpen = te.Literal[
    'com.atproto.admin.defs#reviewOpen'
]  #: Moderator review status of a subject: Open. Indicates that the subject needs to be reviewed by a moderator

ReviewEscalated = te.Literal[
    'com.atproto.admin.defs#reviewEscalated'
]  #: Moderator review status of a subject: Escalated. Indicates that the subject was escalated for review by a moderator

ReviewClosed = te.Literal[
    'com.atproto.admin.defs#reviewClosed'
]  #: Moderator review status of a subject: Closed. Indicates that the subject was already reviewed and resolved by a moderator


class ModEventTakedown(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Take down a subject permanently or temporarily"""

    comment: t.Optional[str] = None  #: Comment.
    duration_in_hours: t.Optional[int] = Field(
        default=None, alias='durationInHours'
    )  #: Indicates how long the takedown should be in effect before automatically expiring.

    py_type: te.Literal['com.atproto.admin.defs#modEventTakedown'] = Field(
        default='com.atproto.admin.defs#modEventTakedown', alias='$type', frozen=True
    )


class ModEventReverseTakedown(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Revert take down action on a subject"""

    comment: t.Optional[str] = None  #: Describe reasoning behind the reversal.

    py_type: te.Literal['com.atproto.admin.defs#modEventReverseTakedown'] = Field(
        default='com.atproto.admin.defs#modEventReverseTakedown', alias='$type', frozen=True
    )


class ModEventComment(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Add a comment to a subject"""

    comment: str  #: Comment.
    sticky: t.Optional[bool] = None  #: Make the comment persistent on the subject.

    py_type: te.Literal['com.atproto.admin.defs#modEventComment'] = Field(
        default='com.atproto.admin.defs#modEventComment', alias='$type', frozen=True
    )


class ModEventReport(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Report a subject"""

    report_type: 'models.ComAtprotoModerationDefs.ReasonType' = Field(alias='reportType')  #: Report type.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['com.atproto.admin.defs#modEventReport'] = Field(
        default='com.atproto.admin.defs#modEventReport', alias='$type', frozen=True
    )


class ModEventLabel(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Apply/Negate labels on a subject"""

    create_label_vals: t.List[str] = Field(alias='createLabelVals')  #: Create label vals.
    negate_label_vals: t.List[str] = Field(alias='negateLabelVals')  #: Negate label vals.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['com.atproto.admin.defs#modEventLabel'] = Field(
        default='com.atproto.admin.defs#modEventLabel', alias='$type', frozen=True
    )


class ModEventAcknowledge(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['com.atproto.admin.defs#modEventAcknowledge'] = Field(
        default='com.atproto.admin.defs#modEventAcknowledge', alias='$type', frozen=True
    )


class ModEventEscalate(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`."""

    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['com.atproto.admin.defs#modEventEscalate'] = Field(
        default='com.atproto.admin.defs#modEventEscalate', alias='$type', frozen=True
    )


class ModEventMute(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Mute incoming reports on a subject"""

    duration_in_hours: int = Field(alias='durationInHours')  #: Indicates how long the subject should remain muted.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['com.atproto.admin.defs#modEventMute'] = Field(
        default='com.atproto.admin.defs#modEventMute', alias='$type', frozen=True
    )


class ModEventUnmute(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Unmute action on a subject"""

    comment: t.Optional[str] = None  #: Describe reasoning behind the reversal.

    py_type: te.Literal['com.atproto.admin.defs#modEventUnmute'] = Field(
        default='com.atproto.admin.defs#modEventUnmute', alias='$type', frozen=True
    )


class ModEventEmail(base.ModelBase):

    """Definition model for :obj:`com.atproto.admin.defs`. Keep a log of outgoing email to a user"""

    subject_line: str = Field(alias='subjectLine')  #: The subject line of the email sent to the user.

    py_type: te.Literal['com.atproto.admin.defs#modEventEmail'] = Field(
        default='com.atproto.admin.defs#modEventEmail', alias='$type', frozen=True
    )
