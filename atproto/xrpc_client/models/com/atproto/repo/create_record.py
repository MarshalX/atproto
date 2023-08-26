##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base, unknown_type


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.createRecord`."""

    collection: str  #: The NSID of the record collection.
    record: 'unknown_type.UnknownType'  #: The record to create.
    repo: str  #: The handle or DID of the repo.
    rkey: t.Optional[str] = None  #: The key of the record.
    swapCommit: t.Optional[str] = None  #: Compare and swap with the previous commit by cid.
    validateAliasMe: t.Optional[bool] = None  #: Validate the record?


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.createRecord`."""

    cid: str  #: Cid.
    uri: str  #: Uri.
