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

    """Parameters model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        cursor: The last known event to backfill from.
    """

    cursor: t.Optional[int] = None


@dataclass
class Commit(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        seq: Seq.
        rebase: Rebase.
        tooBig: Too big.
        repo: Repo.
        commit: Commit.
        prev: Prev.
        blocks: CAR file containing relevant blocks.
        ops: Ops.
        blobs: Blobs.
        time: Time.
    """

    blobs: t.List[CID]
    blocks: t.Union[str, bytes]
    commit: CID
    ops: t.List['models.ComAtprotoSyncSubscribeRepos.RepoOp']
    rebase: bool
    repo: str
    seq: int
    time: str
    tooBig: bool
    prev: t.Optional[CID] = None

    _type: str = 'com.atproto.sync.subscribeRepos#commit'


@dataclass
class Handle(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        seq: Seq.
        did: Did.
        handle: Handle.
        time: Time.
    """

    did: str
    handle: str
    seq: int
    time: str

    _type: str = 'com.atproto.sync.subscribeRepos#handle'


@dataclass
class Migrate(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        seq: Seq.
        did: Did.
        migrateTo: Migrate to.
        time: Time.
    """

    did: str
    seq: int
    time: str
    migrateTo: t.Optional[str] = None

    _type: str = 'com.atproto.sync.subscribeRepos#migrate'


@dataclass
class Tombstone(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        seq: Seq.
        did: Did.
        time: Time.
    """

    did: str
    seq: int
    time: str

    _type: str = 'com.atproto.sync.subscribeRepos#tombstone'


@dataclass
class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        name: Name.
        message: Message.
    """

    name: str
    message: t.Optional[str] = None

    _type: str = 'com.atproto.sync.subscribeRepos#info'


@dataclass
class RepoOp(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        action: Action.
        path: Path.
        cid: Cid.
    """

    action: str
    path: str
    cid: t.Optional[CID] = None

    _type: str = 'com.atproto.sync.subscribeRepos#repoOp'
