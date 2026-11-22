#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base, bytes_type, string_formats


class Commit(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.defs`. Commit to the current state of a space repo. Not signed; authenticated by the repo host with a MAC instead."""

    data: bytes_type.BytesType  #: SHA-256 digest of the repo's LtHash state.
    repo: string_formats.Did  #: Repo.
    rev: string_formats.Tid  #: Rev.
    space: string_formats.SpaceRef  #: Space.
    ver: int  #: Commit format version, currently 1.

    py_type: t.Literal['com.atproto.space.defs#commit'] = Field(
        default='com.atproto.space.defs#commit', alias='$type', frozen=True
    )


class RepoWrite(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.defs`. A repo in the space advanced to a new revision."""

    data: bytes_type.BytesType  #: Data.
    repo: string_formats.Did  #: Repo.
    repo_rev: string_formats.Tid  #: Repo rev.
    space_rev: string_formats.Tid  #: The space revision at which this update was sequenced.
    prev_space_rev: t.Optional[string_formats.Tid] = (
        None  #: The space revision before this update, if any. Set in notifySpaceUpdate, where a gap indicates missed notifications, which can be recovered with listWriters.
    )

    py_type: t.Literal['com.atproto.space.defs#repoWrite'] = Field(
        default='com.atproto.space.defs#repoWrite', alias='$type', frozen=True
    )


class RepoRemoved(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.defs`. A repo was removed from the writer set."""

    repo: string_formats.Did  #: Repo.
    space_rev: string_formats.Tid  #: The space revision at which this update was sequenced.
    prev_space_rev: t.Optional[string_formats.Tid] = (
        None  #: The space revision before this update, if any. Set in notifySpaceUpdate, where a gap indicates missed notifications, which can be recovered with listWriters.
    )

    py_type: t.Literal['com.atproto.space.defs#repoRemoved'] = Field(
        default='com.atproto.space.defs#repoRemoved', alias='$type', frozen=True
    )
