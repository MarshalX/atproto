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

    """Parameters model for :obj:`com.atproto.sync.listRepos`.

    Attributes:
        limit: Limit.
        cursor: Cursor.
    """

    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listRepos`.

    Attributes:
        cursor: Cursor.
        repos: Repos.
    """

    repos: t.List['models.ComAtprotoSyncListRepos.Repo']
    cursor: t.Optional[str] = None


@dataclass
class Repo(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.listRepos`.

    Attributes:
        did: Did.
        head: Head.
    """

    did: str
    head: str

    _type: str = 'com.atproto.sync.listRepos#repo'
