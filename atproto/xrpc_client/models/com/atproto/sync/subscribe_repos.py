##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto import CID
from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.subscribeRepos`."""

    cursor: t.Optional[int] = None  #: The last known event to backfill from.


@dataclass
class Commit(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    blobs: t.List[CID]  #: Blobs.
    blocks: t.Union[str, bytes]  #: CAR file containing relevant blocks.
    commit: CID  #: Commit.
    ops: t.List['models.ComAtprotoSyncSubscribeRepos.RepoOp']  #: Ops.
    rebase: bool  #: Rebase.
    repo: str  #: Repo.
    seq: int  #: Seq.
    time: str  #: Time.
    tooBig: bool  #: Too big.
    prev: t.Optional[CID] = None  #: Prev.

    _type: str = 'com.atproto.sync.subscribeRepos#commit'


@dataclass
class Handle(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    handle: str  #: Handle.
    seq: int  #: Seq.
    time: str  #: Time.

    _type: str = 'com.atproto.sync.subscribeRepos#handle'


@dataclass
class Migrate(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    migrateTo: t.Optional[str] = None  #: Migrate to.

    _type: str = 'com.atproto.sync.subscribeRepos#migrate'


@dataclass
class Tombstone(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.

    _type: str = 'com.atproto.sync.subscribeRepos#tombstone'


@dataclass
class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    name: str  #: Name.
    message: t.Optional[str] = None  #: Message.

    _type: str = 'com.atproto.sync.subscribeRepos#info'


@dataclass
class RepoOp(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    action: str  #: Action.
    path: str  #: Path.
    cid: t.Optional[CID] = None  #: Cid.

    _type: str = 'com.atproto.sync.subscribeRepos#repoOp'
