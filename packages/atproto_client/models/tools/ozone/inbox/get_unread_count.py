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
    """Parameters model for :obj:`tools.ozone.inbox.getUnreadCount`."""

    did: t.Optional[string_formats.Did] = (
        None  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    )
    section: t.Optional[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]] = None  #: Section.


class ParamsDict(t.TypedDict):
    did: te.NotRequired[
        t.Optional[string_formats.Did]
    ]  #: Account to preview. Only Ozone staff can read another account; this does not change its read state.
    section: te.NotRequired[t.Optional[t.Union[t.Literal['reports', 'subjects', 'accountStatus'], str]]]  #: Section.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.inbox.getUnreadCount`."""

    unread_counts: 'models.ToolsOzoneInboxGetUnreadCount.UnreadCounts'  #: Unread counts.


class UnreadCounts(base.ModelBase):
    """Definition model for :obj:`tools.ozone.inbox.getUnreadCount`."""

    total: int = Field(ge=0)  #: Total.
    account_status: te.Annotated[t.Optional[int], Field(ge=0, le=1)] = None  #: Account status.
    reports: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Reports.
    subjects: te.Annotated[t.Optional[int], Field(ge=0)] = None  #: Subjects.

    py_type: t.Literal['tools.ozone.inbox.getUnreadCount#unreadCounts'] = Field(
        default='tools.ozone.inbox.getUnreadCount#unreadCounts', alias='$type', frozen=True
    )
