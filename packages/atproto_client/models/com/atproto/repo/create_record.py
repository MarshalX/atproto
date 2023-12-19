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
    record: 'UnknownInputType'  #: The record to create.
    repo: str  #: The handle or DID of the repo.
    rkey: t.Optional[str] = Field(default=None, max_length=15)  #: The key of the record.
    swap_commit: t.Optional[str] = Field(
        default=None, alias='swapCommit'
    )  #: Compare and swap with the previous commit by CID.
    validate_: t.Optional[bool] = Field(default=True, alias='validate')  #: Flag for validating the record.


class DataDict(te.TypedDict):
    collection: str  #: The NSID of the record collection.
    record: 'UnknownInputType'  #: The record to create.
    repo: str  #: The handle or DID of the repo.
    rkey: te.NotRequired[t.Optional[str]]  #: The key of the record.
    swap_commit: te.NotRequired[t.Optional[str]]  #: Compare and swap with the previous commit by CID.
    validate: te.NotRequired[t.Optional[bool]]  #: Flag for validating the record.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.createRecord`."""

    cid: str  #: Cid.
    uri: str  #: Uri.
