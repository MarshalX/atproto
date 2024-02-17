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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.getRepostedBy`."""

    uri: str  #: Reference (AT-URI) of post record.
    cid: t.Optional[str] = None  #: If supplied, filters to reposts of specific version (by CID) of the post record.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.


class ParamsDict(te.TypedDict):
    uri: str  #: Reference (AT-URI) of post record.
    cid: te.NotRequired[
        t.Optional[str]
    ]  #: If supplied, filters to reposts of specific version (by CID) of the post record.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.getRepostedBy`."""

    reposted_by: t.List['models.AppBskyActorDefs.ProfileView']  #: Reposted by.
    uri: str  #: Uri.
    cid: t.Optional[str] = None  #: Cid.
    cursor: t.Optional[str] = None  #: Cursor.
