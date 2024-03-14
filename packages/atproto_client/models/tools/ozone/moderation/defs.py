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
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class ModEventView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    created_at: str  #: Created at.
    created_by: str  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventDivert',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    id: int  #: Id.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blob_cids: t.List[str]  #: Subject blob cids.
    creator_handle: t.Optional[str] = None  #: Creator handle.
    subject_handle: t.Optional[str] = None  #: Subject handle.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventView'] = Field(
        default='tools.ozone.moderation.defs#modEventView', alias='$type', frozen=True
    )


class ModEventViewDetail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    created_at: str  #: Created at.
    created_by: str  #: Created by.
    event: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.ModEventTakedown',
            'models.ToolsOzoneModerationDefs.ModEventReverseTakedown',
            'models.ToolsOzoneModerationDefs.ModEventComment',
            'models.ToolsOzoneModerationDefs.ModEventReport',
            'models.ToolsOzoneModerationDefs.ModEventLabel',
            'models.ToolsOzoneModerationDefs.ModEventAcknowledge',
            'models.ToolsOzoneModerationDefs.ModEventEscalate',
            'models.ToolsOzoneModerationDefs.ModEventMute',
            'models.ToolsOzoneModerationDefs.ModEventEmail',
            'models.ToolsOzoneModerationDefs.ModEventResolveAppeal',
            'models.ToolsOzoneModerationDefs.ModEventDivert',
        ],
        Field(discriminator='py_type'),
    ]  #: Event.
    id: int  #: Id.
    subject: te.Annotated[
        t.Union[
            'models.ToolsOzoneModerationDefs.RepoView',
            'models.ToolsOzoneModerationDefs.RepoViewNotFound',
            'models.ToolsOzoneModerationDefs.RecordView',
            'models.ToolsOzoneModerationDefs.RecordViewNotFound',
        ],
        Field(discriminator='py_type'),
    ]  #: Subject.
    subject_blobs: t.List['models.ToolsOzoneModerationDefs.BlobView']  #: Subject blobs.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventViewDetail'] = Field(
        default='tools.ozone.moderation.defs#modEventViewDetail', alias='$type', frozen=True
    )


class SubjectStatusView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    created_at: str  #: Timestamp referencing the first moderation status impacting event was emitted on the subject.
    id: int  #: Id.
    review_state: 'models.ToolsOzoneModerationDefs.SubjectReviewState'  #: Review state.
    subject: te.Annotated[
        t.Union['models.ComAtprotoAdminDefs.RepoRef', 'models.ComAtprotoRepoStrongRef.Main'],
        Field(discriminator='py_type'),
    ]  #: Subject.
    updated_at: str  #: Timestamp referencing when the last update was made to the moderation status of the subject.
    appealed: t.Optional[
        bool
    ] = None  #: True indicates that the a previously taken moderator action was appealed against, by the author of the content. False indicates last appeal was resolved by moderators.
    comment: t.Optional[str] = None  #: Sticky comment on the subject.
    last_appealed_at: t.Optional[
        str
    ] = None  #: Timestamp referencing when the author of the subject appealed a moderation action.
    last_reported_at: t.Optional[str] = None  #: Last reported at.
    last_reviewed_at: t.Optional[str] = None  #: Last reviewed at.
    last_reviewed_by: t.Optional[str] = None  #: Last reviewed by.
    mute_until: t.Optional[str] = None  #: Mute until.
    subject_blob_cids: t.Optional[t.List[str]] = None  #: Subject blob cids.
    subject_repo_handle: t.Optional[str] = None  #: Subject repo handle.
    suspend_until: t.Optional[str] = None  #: Suspend until.
    tags: t.Optional[t.List[str]] = None  #: Tags.
    takendown: t.Optional[bool] = None  #: Takendown.

    py_type: te.Literal['tools.ozone.moderation.defs#subjectStatusView'] = Field(
        default='tools.ozone.moderation.defs#subjectStatusView', alias='$type', frozen=True
    )


SubjectReviewState = t.Union[
    'models.ToolsOzoneModerationDefs.ReviewOpen',
    'models.ToolsOzoneModerationDefs.ReviewEscalated',
    'models.ToolsOzoneModerationDefs.ReviewClosed',
    'models.ToolsOzoneModerationDefs.ReviewNone',
]  #: Subject review state

ReviewOpen = te.Literal[
    'tools.ozone.moderation.defs#reviewOpen'
]  #: Moderator review status of a subject: Open. Indicates that the subject needs to be reviewed by a moderator

ReviewEscalated = te.Literal[
    'tools.ozone.moderation.defs#reviewEscalated'
]  #: Moderator review status of a subject: Escalated. Indicates that the subject was escalated for review by a moderator

ReviewClosed = te.Literal[
    'tools.ozone.moderation.defs#reviewClosed'
]  #: Moderator review status of a subject: Closed. Indicates that the subject was already reviewed and resolved by a moderator

ReviewNone = te.Literal[
    'tools.ozone.moderation.defs#reviewNone'
]  #: Moderator review status of a subject: Unnecessary. Indicates that the subject does not need a review at the moment but there is probably some moderation related metadata available for it


class ModEventTakedown(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Take down a subject permanently or temporarily."""

    comment: t.Optional[str] = None  #: Comment.
    duration_in_hours: t.Optional[
        int
    ] = None  #: Indicates how long the takedown should be in effect before automatically expiring.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventTakedown'] = Field(
        default='tools.ozone.moderation.defs#modEventTakedown', alias='$type', frozen=True
    )


class ModEventReverseTakedown(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Revert take down action on a subject."""

    comment: t.Optional[str] = None  #: Describe reasoning behind the reversal.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventReverseTakedown'] = Field(
        default='tools.ozone.moderation.defs#modEventReverseTakedown', alias='$type', frozen=True
    )


class ModEventResolveAppeal(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Resolve appeal on a subject."""

    comment: t.Optional[str] = None  #: Describe resolution.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventResolveAppeal'] = Field(
        default='tools.ozone.moderation.defs#modEventResolveAppeal', alias='$type', frozen=True
    )


class ModEventComment(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Add a comment to a subject."""

    comment: str  #: Comment.
    sticky: t.Optional[bool] = None  #: Make the comment persistent on the subject.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventComment'] = Field(
        default='tools.ozone.moderation.defs#modEventComment', alias='$type', frozen=True
    )


class ModEventReport(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Report a subject."""

    report_type: 'models.ComAtprotoModerationDefs.ReasonType'  #: Report type.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventReport'] = Field(
        default='tools.ozone.moderation.defs#modEventReport', alias='$type', frozen=True
    )


class ModEventLabel(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Apply/Negate labels on a subject."""

    create_label_vals: t.List[str]  #: Create label vals.
    negate_label_vals: t.List[str]  #: Negate label vals.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventLabel'] = Field(
        default='tools.ozone.moderation.defs#modEventLabel', alias='$type', frozen=True
    )


class ModEventAcknowledge(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventAcknowledge'] = Field(
        default='tools.ozone.moderation.defs#modEventAcknowledge', alias='$type', frozen=True
    )


class ModEventEscalate(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventEscalate'] = Field(
        default='tools.ozone.moderation.defs#modEventEscalate', alias='$type', frozen=True
    )


class ModEventMute(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Mute incoming reports on a subject."""

    duration_in_hours: int  #: Indicates how long the subject should remain muted.
    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventMute'] = Field(
        default='tools.ozone.moderation.defs#modEventMute', alias='$type', frozen=True
    )


class ModEventUnmute(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Unmute action on a subject."""

    comment: t.Optional[str] = None  #: Describe reasoning behind the reversal.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventUnmute'] = Field(
        default='tools.ozone.moderation.defs#modEventUnmute', alias='$type', frozen=True
    )


class ModEventEmail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Keep a log of outgoing email to a user."""

    subject_line: str  #: The subject line of the email sent to the user.
    comment: t.Optional[str] = None  #: Additional comment about the outgoing comm.
    content: t.Optional[str] = None  #: The content of the email sent to the user.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventEmail'] = Field(
        default='tools.ozone.moderation.defs#modEventEmail', alias='$type', frozen=True
    )


class ModEventDivert(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Divert a record's blobs to a 3rd party service for further scanning/tagging."""

    comment: t.Optional[str] = None  #: Comment.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventDivert'] = Field(
        default='tools.ozone.moderation.defs#modEventDivert', alias='$type', frozen=True
    )


class ModEventTag(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`. Add/Remove a tag on a subject."""

    add: t.List[str]  #: Tags to be added to the subject. If already exists, won't be duplicated.
    remove: t.List[str]  #: Tags to be removed to the subject. Ignores a tag If it doesn't exist, won't be duplicated.
    comment: t.Optional[str] = None  #: Additional comment about added/removed tags.

    py_type: te.Literal['tools.ozone.moderation.defs#modEventTag'] = Field(
        default='tools.ozone.moderation.defs#modEventTag', alias='$type', frozen=True
    )


class RepoView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str  #: Indexed at.
    moderation: 'models.ToolsOzoneModerationDefs.Moderation'  #: Moderation.
    related_records: t.List['UnknownType']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    invite_note: t.Optional[str] = None  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invites_disabled: t.Optional[bool] = None  #: Invites disabled.

    py_type: te.Literal['tools.ozone.moderation.defs#repoView'] = Field(
        default='tools.ozone.moderation.defs#repoView', alias='$type', frozen=True
    )


class RepoViewDetail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    did: str  #: Did.
    handle: str  #: Handle.
    indexed_at: str  #: Indexed at.
    moderation: 'models.ToolsOzoneModerationDefs.ModerationDetail'  #: Moderation.
    related_records: t.List['UnknownType']  #: Related records.
    email: t.Optional[str] = None  #: Email.
    email_confirmed_at: t.Optional[str] = None  #: Email confirmed at.
    invite_note: t.Optional[str] = None  #: Invite note.
    invited_by: t.Optional['models.ComAtprotoServerDefs.InviteCode'] = None  #: Invited by.
    invites: t.Optional[t.List['models.ComAtprotoServerDefs.InviteCode']] = None  #: Invites.
    invites_disabled: t.Optional[bool] = None  #: Invites disabled.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['tools.ozone.moderation.defs#repoViewDetail'] = Field(
        default='tools.ozone.moderation.defs#repoViewDetail', alias='$type', frozen=True
    )


class RepoViewNotFound(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    did: str  #: Did.

    py_type: te.Literal['tools.ozone.moderation.defs#repoViewNotFound'] = Field(
        default='tools.ozone.moderation.defs#repoViewNotFound', alias='$type', frozen=True
    )


class RecordView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    blob_cids: t.List[str]  #: Blob cids.
    cid: str  #: Cid.
    indexed_at: str  #: Indexed at.
    moderation: 'models.ToolsOzoneModerationDefs.Moderation'  #: Moderation.
    repo: 'models.ToolsOzoneModerationDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'UnknownType'  #: Value.

    py_type: te.Literal['tools.ozone.moderation.defs#recordView'] = Field(
        default='tools.ozone.moderation.defs#recordView', alias='$type', frozen=True
    )


class RecordViewDetail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    blobs: t.List['models.ToolsOzoneModerationDefs.BlobView']  #: Blobs.
    cid: str  #: Cid.
    indexed_at: str  #: Indexed at.
    moderation: 'models.ToolsOzoneModerationDefs.ModerationDetail'  #: Moderation.
    repo: 'models.ToolsOzoneModerationDefs.RepoView'  #: Repo.
    uri: str  #: Uri.
    value: 'UnknownType'  #: Value.
    labels: t.Optional[t.List['models.ComAtprotoLabelDefs.Label']] = None  #: Labels.

    py_type: te.Literal['tools.ozone.moderation.defs#recordViewDetail'] = Field(
        default='tools.ozone.moderation.defs#recordViewDetail', alias='$type', frozen=True
    )


class RecordViewNotFound(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    uri: str  #: Uri.

    py_type: te.Literal['tools.ozone.moderation.defs#recordViewNotFound'] = Field(
        default='tools.ozone.moderation.defs#recordViewNotFound', alias='$type', frozen=True
    )


class Moderation(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    subject_status: t.Optional['models.ToolsOzoneModerationDefs.SubjectStatusView'] = None  #: Subject status.

    py_type: te.Literal['tools.ozone.moderation.defs#moderation'] = Field(
        default='tools.ozone.moderation.defs#moderation', alias='$type', frozen=True
    )


class ModerationDetail(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    subject_status: t.Optional['models.ToolsOzoneModerationDefs.SubjectStatusView'] = None  #: Subject status.

    py_type: te.Literal['tools.ozone.moderation.defs#moderationDetail'] = Field(
        default='tools.ozone.moderation.defs#moderationDetail', alias='$type', frozen=True
    )


class BlobView(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    cid: str  #: Cid.
    created_at: str  #: Created at.
    mime_type: str  #: Mime type.
    size: int  #: Size.
    details: t.Optional[
        te.Annotated[
            t.Union['models.ToolsOzoneModerationDefs.ImageDetails', 'models.ToolsOzoneModerationDefs.VideoDetails'],
            Field(default=None, discriminator='py_type'),
        ]
    ] = None  #: Details.
    moderation: t.Optional['models.ToolsOzoneModerationDefs.Moderation'] = None  #: Moderation.

    py_type: te.Literal['tools.ozone.moderation.defs#blobView'] = Field(
        default='tools.ozone.moderation.defs#blobView', alias='$type', frozen=True
    )


class ImageDetails(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    height: int  #: Height.
    width: int  #: Width.

    py_type: te.Literal['tools.ozone.moderation.defs#imageDetails'] = Field(
        default='tools.ozone.moderation.defs#imageDetails', alias='$type', frozen=True
    )


class VideoDetails(base.ModelBase):
    """Definition model for :obj:`tools.ozone.moderation.defs`."""

    height: int  #: Height.
    length: int  #: Length.
    width: int  #: Width.

    py_type: te.Literal['tools.ozone.moderation.defs#videoDetails'] = Field(
        default='tools.ozone.moderation.defs#videoDetails', alias='$type', frozen=True
    )
