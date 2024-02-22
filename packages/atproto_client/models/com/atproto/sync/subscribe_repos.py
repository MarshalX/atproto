##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_core.cid import CIDType

    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.sync.subscribeRepos`."""

    cursor: t.Optional[int] = None  #: The last known event seq number to backfill from.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[int]]  #: The last known event seq number to backfill from.


class Commit(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents an update of repository state. Note that empty commits are allowed, which include no repo data changes, but an update to rev and signature."""

    blobs: t.List['CIDType']  #: Blobs.
    blocks: t.Union[str, bytes]  #: CAR file containing relevant blocks, as a diff since the previous repo state.
    commit: 'CIDType'  #: Repo commit object CID.
    ops: t.List['models.ComAtprotoSyncSubscribeRepos.RepoOp'] = Field(max_length=200)  #: Ops.
    rebase: bool  #: DEPRECATED -- unused.
    repo: str  #: The repo this event comes from.
    rev: str  #: The rev of the emitted commit. Note that this information is also in the commit object included in blocks, unless this is a tooBig event.
    seq: int  #: The stream sequence number of this message.
    time: str  #: Timestamp of when this message was originally broadcast.
    too_big: bool  #: Indicates that this commit contained too many ops, or data size was too large. Consumers will need to make a separate request to get missing data.
    prev: t.Optional[
        'CIDType'
    ] = (
        None
    )  #: DEPRECATED -- unused. WARNING -- nullable and optional; stick with optional to ensure golang interoperability.
    since: t.Optional[str] = None  #: The rev of the last emitted commit from this repo (if any).

    py_type: te.Literal['com.atproto.sync.subscribeRepos#commit'] = Field(
        default='com.atproto.sync.subscribeRepos#commit', alias='$type', frozen=True
    )


class Identity(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents a change to an account's identity. Could be an updated handle, signing key, or pds hosting endpoint. Serves as a prod to all downstream services to refresh their identity cache."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#identity'] = Field(
        default='com.atproto.sync.subscribeRepos#identity', alias='$type', frozen=True
    )


class Handle(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents an update of the account's handle, or transition to/from invalid state. NOTE: Will be deprecated in favor of #identity."""

    did: str  #: Did.
    handle: str  #: Handle.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#handle'] = Field(
        default='com.atproto.sync.subscribeRepos#handle', alias='$type', frozen=True
    )


class Migrate(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents an account moving from one PDS instance to another. NOTE: not implemented; account migration uses #identity instead."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    migrate_to: t.Optional[str] = None  #: Migrate to.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#migrate'] = Field(
        default='com.atproto.sync.subscribeRepos#migrate', alias='$type', frozen=True
    )


class Tombstone(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Indicates that an account has been deleted. NOTE: may be deprecated in favor of #identity or a future #account event."""

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
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. A repo operation, ie a mutation of a single record."""

    action: str  #: Action.
    path: str  #: Path.
    cid: t.Optional['CIDType'] = None  #: For creates and updates, the new record CID. For deletions, null.

    py_type: te.Literal['com.atproto.sync.subscribeRepos#repoOp'] = Field(
        default='com.atproto.sync.subscribeRepos#repoOp', alias='$type', frozen=True
    )
