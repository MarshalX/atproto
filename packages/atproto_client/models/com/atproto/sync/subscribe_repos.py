##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2024 Ilya (Marshal) <https://github.com/MarshalX>.
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


class ParamsDict(t.TypedDict):
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
    prev: t.Optional['CIDType'] = (
        None  #: DEPRECATED -- unused. WARNING -- nullable and optional; stick with optional to ensure golang interoperability.
    )
    since: t.Optional[str] = None  #: The rev of the last emitted commit from this repo (if any).

    py_type: t.Literal['com.atproto.sync.subscribeRepos#commit'] = Field(
        default='com.atproto.sync.subscribeRepos#commit', alias='$type', frozen=True
    )


class Identity(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents a change to an account's identity. Could be an updated handle, signing key, or pds hosting endpoint. Serves as a prod to all downstream services to refresh their identity cache."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    handle: t.Optional[str] = (
        None  #: The current handle for the account, or 'handle.invalid' if validation fails. This field is optional, might have been validated or passed-through from an upstream source. Semantics and behaviors for PDS vs Relay may evolve in the future; see atproto specs for more details.
    )

    py_type: t.Literal['com.atproto.sync.subscribeRepos#identity'] = Field(
        default='com.atproto.sync.subscribeRepos#identity', alias='$type', frozen=True
    )


class Account(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. Represents a change to an account's status on a host (eg, PDS or Relay). The semantics of this event are that the status is at the host which emitted the event, not necessarily that at the currently active PDS. Eg, a Relay takedown would emit a takedown with active=false, even if the PDS is still active."""

    active: (
        bool  #: Indicates that the account has a repository which can be fetched from the host that emitted this event.
    )
    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    status: t.Optional[
        t.Union[t.Literal['takendown'], t.Literal['suspended'], t.Literal['deleted'], t.Literal['deactivated'], str]
    ] = None  #: If active=false, this optional field indicates a reason for why the account is not active.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#account'] = Field(
        default='com.atproto.sync.subscribeRepos#account', alias='$type', frozen=True
    )


class Handle(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. DEPRECATED -- Use #identity event instead."""

    did: str  #: Did.
    handle: str  #: Handle.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#handle'] = Field(
        default='com.atproto.sync.subscribeRepos#handle', alias='$type', frozen=True
    )


class Migrate(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. DEPRECATED -- Use #account event instead."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.
    migrate_to: t.Optional[str] = None  #: Migrate to.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#migrate'] = Field(
        default='com.atproto.sync.subscribeRepos#migrate', alias='$type', frozen=True
    )


class Tombstone(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. DEPRECATED -- Use #account event instead."""

    did: str  #: Did.
    seq: int  #: Seq.
    time: str  #: Time.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#tombstone'] = Field(
        default='com.atproto.sync.subscribeRepos#tombstone', alias='$type', frozen=True
    )


class Info(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`."""

    name: t.Union[t.Literal['OutdatedCursor'], str]  #: Name.
    message: t.Optional[str] = None  #: Message.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#info'] = Field(
        default='com.atproto.sync.subscribeRepos#info', alias='$type', frozen=True
    )


class RepoOp(base.ModelBase):
    """Definition model for :obj:`com.atproto.sync.subscribeRepos`. A repo operation, ie a mutation of a single record."""

    action: t.Union[t.Literal['create'], t.Literal['update'], t.Literal['delete'], str]  #: Action.
    path: str  #: Path.
    cid: t.Optional['CIDType'] = None  #: For creates and updates, the new record CID. For deletions, null.

    py_type: t.Literal['com.atproto.sync.subscribeRepos#repoOp'] = Field(
        default='com.atproto.sync.subscribeRepos#repoOp', alias='$type', frozen=True
    )
