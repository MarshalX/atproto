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

    """Parameters model for :obj:`com.atproto.sync.listRepos`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=500, ge=1, le=1000)  #: Limit.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listRepos`."""

    repos: t.List['models.ComAtprotoSyncListRepos.Repo']  #: Repos.
    cursor: t.Optional[str] = None  #: Cursor.


class Repo(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.listRepos`."""

    did: str  #: Did.
    head: str  #: Head.
    rev: str  #: Rev.

    py_type: te.Literal['com.atproto.sync.listRepos#repo'] = Field(
        default='com.atproto.sync.listRepos#repo', alias='$type', frozen=True
    )
