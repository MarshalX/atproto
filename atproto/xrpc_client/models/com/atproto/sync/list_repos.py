##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.listRepos`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = None  #: Limit.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listRepos`."""

    repos: t.List['models.ComAtprotoSyncListRepos.Repo']  #: Repos.
    cursor: t.Optional[str] = None  #: Cursor.


class Repo(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.listRepos`."""

    did: str  #: Did.
    head: str  #: Head.

    _type: str = 'com.atproto.sync.listRepos#repo'
