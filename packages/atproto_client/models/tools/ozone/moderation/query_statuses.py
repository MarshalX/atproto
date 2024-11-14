##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.moderation.queryStatuses`."""

    appealed: t.Optional[bool] = None  #: Get subjects in unresolved appealed status.
    collections: t.Optional[t.List[str]] = Field(
        default=None, max_length=20
    )  #: If specified, subjects belonging to the given collections will be returned. When subjectType is set to 'account', this will be ignored.
    comment: t.Optional[str] = None  #: Search subjects by keyword from comments.
    cursor: t.Optional[str] = None  #: Cursor.
    exclude_tags: t.Optional[t.List[str]] = None  #: Exclude tags.
    hosting_deleted_after: t.Optional[str] = (
        None  #: Search subjects where the associated record/account was deleted after a given timestamp.
    )
    hosting_deleted_before: t.Optional[str] = (
        None  #: Search subjects where the associated record/account was deleted before a given timestamp.
    )
    hosting_statuses: t.Optional[t.List[str]] = None  #: Search subjects by the status of the associated record/account.
    hosting_updated_after: t.Optional[str] = (
        None  #: Search subjects where the associated record/account was updated after a given timestamp.
    )
    hosting_updated_before: t.Optional[str] = (
        None  #: Search subjects where the associated record/account was updated before a given timestamp.
    )
    ignore_subjects: t.Optional[t.List[str]] = None  #: Ignore subjects.
    include_all_user_records: t.Optional[bool] = (
        None  #: All subjects, or subjects from given 'collections' param, belonging to the account specified in the 'subject' param will be returned.
    )
    include_muted: t.Optional[bool] = (
        None  #: By default, we don't include muted subjects in the results. Set this to true to include them.
    )
    last_reviewed_by: t.Optional[str] = None  #: Get all subject statuses that were reviewed by a specific moderator.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    only_muted: t.Optional[bool] = None  #: When set to true, only muted subjects and reporters will be returned.
    reported_after: t.Optional[str] = None  #: Search subjects reported after a given timestamp.
    reported_before: t.Optional[str] = None  #: Search subjects reported before a given timestamp.
    review_state: t.Optional[str] = None  #: Specify when fetching subjects in a certain state.
    reviewed_after: t.Optional[str] = None  #: Search subjects reviewed after a given timestamp.
    reviewed_before: t.Optional[str] = None  #: Search subjects reviewed before a given timestamp.
    sort_direction: t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]] = 'desc'  #: Sort direction.
    sort_field: t.Optional[t.Union[t.Literal['lastReviewedAt'], t.Literal['lastReportedAt']]] = (
        'lastReportedAt'  #: Sort field.
    )
    subject: t.Optional[str] = None  #: The subject to get the status for.
    subject_type: t.Optional[t.Union[t.Literal['account'], t.Literal['record'], str]] = (
        None  #: If specified, subjects of the given type (account or record) will be returned. When this is set to 'account' the 'collections' parameter will be ignored. When includeAllUserRecords or subject is set, this will be ignored.
    )
    tags: t.Optional[t.List[str]] = None  #: Tags.
    takendown: t.Optional[bool] = None  #: Get subjects that were taken down.


class ParamsDict(t.TypedDict):
    appealed: te.NotRequired[t.Optional[bool]]  #: Get subjects in unresolved appealed status.
    collections: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: If specified, subjects belonging to the given collections will be returned. When subjectType is set to 'account', this will be ignored.
    comment: te.NotRequired[t.Optional[str]]  #: Search subjects by keyword from comments.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    exclude_tags: te.NotRequired[t.Optional[t.List[str]]]  #: Exclude tags.
    hosting_deleted_after: te.NotRequired[
        t.Optional[str]
    ]  #: Search subjects where the associated record/account was deleted after a given timestamp.
    hosting_deleted_before: te.NotRequired[
        t.Optional[str]
    ]  #: Search subjects where the associated record/account was deleted before a given timestamp.
    hosting_statuses: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Search subjects by the status of the associated record/account.
    hosting_updated_after: te.NotRequired[
        t.Optional[str]
    ]  #: Search subjects where the associated record/account was updated after a given timestamp.
    hosting_updated_before: te.NotRequired[
        t.Optional[str]
    ]  #: Search subjects where the associated record/account was updated before a given timestamp.
    ignore_subjects: te.NotRequired[t.Optional[t.List[str]]]  #: Ignore subjects.
    include_all_user_records: te.NotRequired[
        t.Optional[bool]
    ]  #: All subjects, or subjects from given 'collections' param, belonging to the account specified in the 'subject' param will be returned.
    include_muted: te.NotRequired[
        t.Optional[bool]
    ]  #: By default, we don't include muted subjects in the results. Set this to true to include them.
    last_reviewed_by: te.NotRequired[
        t.Optional[str]
    ]  #: Get all subject statuses that were reviewed by a specific moderator.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    only_muted: te.NotRequired[
        t.Optional[bool]
    ]  #: When set to true, only muted subjects and reporters will be returned.
    reported_after: te.NotRequired[t.Optional[str]]  #: Search subjects reported after a given timestamp.
    reported_before: te.NotRequired[t.Optional[str]]  #: Search subjects reported before a given timestamp.
    review_state: te.NotRequired[t.Optional[str]]  #: Specify when fetching subjects in a certain state.
    reviewed_after: te.NotRequired[t.Optional[str]]  #: Search subjects reviewed after a given timestamp.
    reviewed_before: te.NotRequired[t.Optional[str]]  #: Search subjects reviewed before a given timestamp.
    sort_direction: te.NotRequired[t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]]]  #: Sort direction.
    sort_field: te.NotRequired[
        t.Optional[t.Union[t.Literal['lastReviewedAt'], t.Literal['lastReportedAt']]]
    ]  #: Sort field.
    subject: te.NotRequired[t.Optional[str]]  #: The subject to get the status for.
    subject_type: te.NotRequired[
        t.Optional[t.Union[t.Literal['account'], t.Literal['record'], str]]
    ]  #: If specified, subjects of the given type (account or record) will be returned. When this is set to 'account' the 'collections' parameter will be ignored. When includeAllUserRecords or subject is set, this will be ignored.
    tags: te.NotRequired[t.Optional[t.List[str]]]  #: Tags.
    takendown: te.NotRequired[t.Optional[bool]]  #: Get subjects that were taken down.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.moderation.queryStatuses`."""

    subject_statuses: t.List['models.ToolsOzoneModerationDefs.SubjectStatusView']  #: Subject statuses.
    cursor: t.Optional[str] = None  #: Cursor.
