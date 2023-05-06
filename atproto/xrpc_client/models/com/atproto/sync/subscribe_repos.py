##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional, Union

from atproto import CID
from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


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

    blobs: List[CID]
    blocks: Union[str, bytes]
    commit: CID
    ops: List['models.ComAtprotoSyncSubscribeRepos.RepoOp']
    rebase: bool
    repo: str
    seq: int
    time: str
    tooBig: bool
    prev: Optional[CID] = None


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
    migrateTo: Optional[str] = None


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


@dataclass
class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`.

    Attributes:
        name: Name.
        message: Message.
    """

    name: str
    message: Optional[str] = None


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
    cid: Optional[CID] = None
