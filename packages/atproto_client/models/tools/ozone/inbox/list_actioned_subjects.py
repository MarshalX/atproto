#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.inbox.listActionedSubjects`."""

    cursor: t.Optional[str] = None  #: An opaque cursor for pagination.
    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    )
    filter: t.Optional[t.Literal['all', 'pending', 'resolved', 'unread']] = (
        'all'  #: Filter subject activity. pending includes subjects whose latest appeal report is not closed; resolved includes subjects whose latest appeal report is closed. unread includes subjects whose public updatedAt is after the subjects section's seenAt watermark.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Limit.
    sort_direction: t.Optional[t.Literal['asc', 'desc']] = 'desc'  #: Sort direction.
    sort_field: t.Optional[t.Literal['createdAt', 'updatedAt']] = 'updatedAt'  #: Sort field.


class ParamsDict(t.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: An opaque cursor for pagination.
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Defaults to the authenticated account; another account requires an active moderator, triage, or admin credential.
    filter: te.NotRequired[
        t.Optional[t.Literal['all', 'pending', 'resolved', 'unread']]
    ]  #: Filter subject activity. pending includes subjects whose latest appeal report is not closed; resolved includes subjects whose latest appeal report is closed. unread includes subjects whose public updatedAt is after the subjects section's seenAt watermark.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    sort_direction: te.NotRequired[t.Optional[t.Literal['asc', 'desc']]]  #: Sort direction.
    sort_field: te.NotRequired[t.Optional[t.Literal['createdAt', 'updatedAt']]]  #: Sort field.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.listActionedSubjects`."""

    subjects: t.List['models.ToolsOzoneInboxDefs.SubjectView']  #: Subjects.
    cursor: t.Optional[str] = None  #: Cursor.
