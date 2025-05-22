##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`tools.ozone.verification.listVerifications`."""

    created_after: t.Optional[string_formats.DateTime] = None  #: Filter to verifications created after this timestamp.
    created_before: t.Optional[string_formats.DateTime] = (
        None  #: Filter to verifications created before this timestamp.
    )
    cursor: t.Optional[str] = None  #: Pagination cursor.
    is_revoked: t.Optional[bool] = None  #: Filter to verifications that are revoked or not. By default, includes both.
    issuers: t.Optional[t.List[string_formats.Did]] = Field(
        default=None, max_length=100
    )  #: Filter to verifications from specific issuers.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Maximum number of results to return.
    sort_direction: t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]] = (
        'desc'  #: Sort direction for creation date.
    )
    subjects: t.Optional[t.List[string_formats.Did]] = Field(
        default=None, max_length=100
    )  #: Filter to specific verified DIDs.


class ParamsDict(t.TypedDict):
    created_after: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Filter to verifications created after this timestamp.
    created_before: te.NotRequired[
        t.Optional[string_formats.DateTime]
    ]  #: Filter to verifications created before this timestamp.
    cursor: te.NotRequired[t.Optional[str]]  #: Pagination cursor.
    is_revoked: te.NotRequired[
        t.Optional[bool]
    ]  #: Filter to verifications that are revoked or not. By default, includes both.
    issuers: te.NotRequired[t.Optional[t.List[string_formats.Did]]]  #: Filter to verifications from specific issuers.
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of results to return.
    sort_direction: te.NotRequired[
        t.Optional[t.Union[t.Literal['asc'], t.Literal['desc']]]
    ]  #: Sort direction for creation date.
    subjects: te.NotRequired[t.Optional[t.List[string_formats.Did]]]  #: Filter to specific verified DIDs.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`tools.ozone.verification.listVerifications`."""

    verifications: t.List['models.ToolsOzoneVerificationDefs.VerificationView']  #: Verifications.
    cursor: t.Optional[str] = None  #: Cursor.
