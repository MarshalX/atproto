##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto import CIDType
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.subscribeRepos`."""

    cursor: t.Optional[int] = None  #: The last known event to backfill from.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[int]]  #: The last known event to backfill from.


class Commit(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    blobs: t.List['CIDType']  #: Blobs.
    blocks: t.Union[str, bytes]  #: CAR file containing relevant blocks.
    commit: 'CIDType'  #: Commit.
    ops: t.List['models.ComAtprotoSyncSubscribeRepos.RepoOp'] = Field(max_length=200)  #: Ops.
    rebase: bool  #: Rebase.
    repo: str  #: Repo.
    rev: str  #: The rev of the emitted commit.
    seq: int  #: Seq.
    time: str  #: Time.
    too_big: bool = Field(alias='tooBig')  #: Too big.
    prev: t.Optional['CIDType'] = None  #: Prev.
    since: t.Optional[str] = None  #: The rev of the last emitted commit from this repo.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#commit'] = Field(
        default='com.atproto.sync.subscribeRepos#commit', alias='$type', frozen=True
    )


class Handle(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    handle: str  #: Handle.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#handle'] = Field(
        default='com.atproto.sync.subscribeRepos#handle', alias='$type', frozen=True
    )


class Migrate(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    migrate_to: t.Optional[str] = Field(default=None, alias='migrateTo')  #: Migrate to.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#migrate'] = Field(
        default='com.atproto.sync.subscribeRepos#migrate', alias='$type', frozen=True
    )


class Tombstone(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#tombstone'] = Field(
        default='com.atproto.sync.subscribeRepos#tombstone', alias='$type', frozen=True
    )


class Info(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    name: str  #: Name.
    message: t.Optional[str] = None  #: Message.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#info'] = Field(
        default='com.atproto.sync.subscribeRepos#info', alias='$type', frozen=True
    )


class RepoOp(base.ModelBase):

    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. A repo operation, ie a write of a single record. For creates and updates, CID is the record's CID as of this operation. For deletes, it's null."""

    action: str  #: Action.
    path: str  #: Path.
    cid: t.Optional['CIDType'] = None  #: Cid.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#repoOp'] = Field(
        default='com.atproto.sync.subscribeRepos#repoOp', alias='$type', frozen=True
    )
