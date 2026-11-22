#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.space.getRecord`."""

    collection: string_formats.Nsid  #: Collection.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.


class ParamsDict(t.TypedDict):
    collection: string_formats.Nsid  #: Collection.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.getRecord`."""

    cid: string_formats.Cid  #: Cid.
    uri: string_formats.AtUri  #: Uri.
    value: 'UnknownType'  #: Value.
