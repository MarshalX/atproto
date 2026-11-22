#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.deleteRecord`."""

    collection: string_formats.Nsid  #: Collection.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.


class DataDict(t.TypedDict):
    collection: string_formats.Nsid  #: Collection.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.deleteRecord`."""
