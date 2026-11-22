#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownInputType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.putRecord`."""

    collection: string_formats.Nsid  #: Collection.
    record: 'UnknownInputType'  #: Record.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.
    validate_: t.Optional[bool] = (
        None  #: Can be set to 'false' to skip Lexicon schema validation of record data, 'true' to require it, or leave unset to validate only for known Lexicons.
    )


class DataDict(t.TypedDict):
    collection: string_formats.Nsid  #: Collection.
    record: 'UnknownInputType'  #: Record.
    repo: string_formats.Did  #: Repo.
    rkey: string_formats.RecordKey  #: Rkey.
    space: string_formats.SpaceRef  #: Space.
    validate_: te.NotRequired[
        t.Optional[bool]
    ]  #: Can be set to 'false' to skip Lexicon schema validation of record data, 'true' to require it, or leave unset to validate only for known Lexicons.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.putRecord`."""

    cid: string_formats.Cid  #: Cid.
    uri: string_formats.AtUri  #: Uri.
    validation_status: t.Optional[t.Union[t.Literal['valid', 'unknown'], str]] = None  #: Validation status.
