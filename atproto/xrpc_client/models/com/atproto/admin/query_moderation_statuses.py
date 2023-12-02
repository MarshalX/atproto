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


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.queryModerationStatuses`."""

    comment: t.Optional[str] = None  #: Search subjects by keyword from comments.
    cursor: t.Optional[str] = None  #: Cursor.
    ignore_subjects: t.Optional[t.List[str]] = Field(default=None, alias='ignoreSubjects')  #: Ignore subjects.
    include_muted: t.Optional[bool] = Field(
        default=None, alias='includeMuted'
    )  #: By default, we don't include muted subjects in the results. Set this to true to include them.
    last_reviewed_by: t.Optional[str] = Field(
        default=None, alias='lastReviewedBy'
    )  #: Get all subject statuses that were reviewed by a specific moderator.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    reported_after: t.Optional[str] = Field(
        default=None, alias='reportedAfter'
    )  #: Search subjects reported after a given timestamp.
    reported_before: t.Optional[str] = Field(
        default=None, alias='reportedBefore'
    )  #: Search subjects reported before a given timestamp.
    review_state: t.Optional[str] = Field(
        default=None, alias='reviewState'
    )  #: Specify when fetching subjects in a certain state.
    reviewed_after: t.Optional[str] = Field(
        default=None, alias='reviewedAfter'
    )  #: Search subjects reviewed after a given timestamp.
    reviewed_before: t.Optional[str] = Field(
        default=None, alias='reviewedBefore'
    )  #: Search subjects reviewed before a given timestamp.
    sort_direction: t.Optional[str] = Field(default='desc', alias='sortDirection')  #: Sort direction.
    sort_field: t.Optional[str] = Field(default='lastReportedAt', alias='sortField')  #: Sort field.
    subject: t.Optional[str] = None  #: Subject.
    takendown: t.Optional[bool] = None  #: Get subjects that were taken down.


class ParamsDict(te.TypedDict):
    comment: te.NotRequired[t.Optional[str]]  #: Search subjects by keyword from comments.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    ignore_subjects: te.NotRequired[t.Optional[t.List[str]]]  #: Ignore subjects.
    include_muted: te.NotRequired[
        t.Optional[bool]
    ]  #: By default, we don't include muted subjects in the results. Set this to true to include them.
    last_reviewed_by: te.NotRequired[
        t.Optional[str]
    ]  #: Get all subject statuses that were reviewed by a specific moderator.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    reported_after: te.NotRequired[t.Optional[str]]  #: Search subjects reported after a given timestamp.
    reported_before: te.NotRequired[t.Optional[str]]  #: Search subjects reported before a given timestamp.
    review_state: te.NotRequired[t.Optional[str]]  #: Specify when fetching subjects in a certain state.
    reviewed_after: te.NotRequired[t.Optional[str]]  #: Search subjects reviewed after a given timestamp.
    reviewed_before: te.NotRequired[t.Optional[str]]  #: Search subjects reviewed before a given timestamp.
    sort_direction: te.NotRequired[t.Optional[str]]  #: Sort direction.
    sort_field: te.NotRequired[t.Optional[str]]  #: Sort field.
    subject: te.NotRequired[t.Optional[str]]  #: Subject.
    takendown: te.NotRequired[t.Optional[bool]]  #: Get subjects that were taken down.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.queryModerationStatuses`."""

    subject_statuses: t.List['models.ComAtprotoAdminDefs.SubjectStatusView'] = Field(
        alias='subjectStatuses'
    )  #: Subject statuses.
    cursor: t.Optional[str] = None  #: Cursor.
