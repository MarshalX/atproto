##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.unknown_type import UnknownType
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.createRecord`."""

    collection: str  #: The NSID of the record collection.
    record: 'UnknownType'  #: The record to create.
    repo: str  #: The handle or DID of the repo.
    rkey: t.Optional[str] = Field(default=None, max_length=15)  #: The key of the record.
    swap_commit: t.Optional[str] = Field(
        default=None, alias='swapCommit'
    )  #: Compare and swap with the previous commit by cid.
    validate_: t.Optional[bool] = Field(default=True, alias='validate')  #: Validate the record?


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.createRecord`."""

    cid: str  #: Cid.
    uri: str  #: Uri.
