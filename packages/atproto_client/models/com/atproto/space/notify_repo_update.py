#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base, bytes_type, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.notifyRepoUpdate`."""

    data: bytes_type.BytesType  #: Data.
    repo: string_formats.Did  #: Repo.
    repo_rev: string_formats.Tid  #: Repo rev.
    space: string_formats.SpaceRef  #: Space.


class DataDict(t.TypedDict):
    data: bytes_type.BytesType  #: Data.
    repo: string_formats.Did  #: Repo.
    repo_rev: string_formats.Tid  #: Repo rev.
    space: string_formats.SpaceRef  #: Space.
