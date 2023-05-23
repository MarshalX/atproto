##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.admin.searchRepos`."""

    cursor: t.Optional[str] = None  #: Cursor.
    invitedBy: t.Optional[str] = None  #: Invited by.
    limit: t.Optional[int] = None  #: Limit.
    term: t.Optional[str] = None  #: Term.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.admin.searchRepos`."""

    repos: t.List['models.ComAtprotoAdminDefs.RepoView']  #: Repos.
    cursor: t.Optional[str] = None  #: Cursor.
