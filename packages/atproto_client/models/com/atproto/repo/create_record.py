##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownInputType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.repo.createRecord`."""

    collection: str  #: The NSID of the record collection.
    record: 'UnknownInputType'  #: The record itself. Must contain a $type field.
    repo: str  #: The handle or DID of the repo (aka, current account).
    rkey: t.Optional[str] = Field(default=None, max_length=15)  #: The Record Key.
    swap_commit: t.Optional[str] = None  #: Compare and swap with the previous commit by CID.
    validate_: t.Optional[bool] = None  #: Can be set to 'false' to skip Lexicon schema validation of record data.


class DataDict(te.TypedDict):
    collection: str  #: The NSID of the record collection.
    record: 'UnknownInputType'  #: The record itself. Must contain a $type field.
    repo: str  #: The handle or DID of the repo (aka, current account).
    rkey: te.NotRequired[t.Optional[str]]  #: The Record Key.
    swap_commit: te.NotRequired[t.Optional[str]]  #: Compare and swap with the previous commit by CID.
    validate: te.NotRequired[
        t.Optional[bool]
    ]  #: Can be set to 'false' to skip Lexicon schema validation of record data.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.repo.createRecord`."""

    cid: str  #: Cid.
    uri: str  #: Uri.
