##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.searchRepos`."""

    cursor: t.Optional[str] = None  #: Cursor.
    invited_by: t.Optional[str] = Field(default=None, alias='invitedBy')  #: Invited by.
    limit: t.Optional[int] = Field(default=50, ge=1, le=100)  #: Limit.
    term: t.Optional[str] = None  #: Term.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.searchRepos`."""

    repos: t.List['models.ComAtprotoAdminDefs.RepoView']  #: Repos.
    cursor: t.Optional[str] = None  #: Cursor.
