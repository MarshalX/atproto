##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.listRecords`."""

    collection: str  #: The NSID of the record type.
    repo: str  #: The handle or DID of the repo.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = None  #: The number of records to return.
    reverse: t.Optional[bool] = None  #: Reverse the order of the returned records?
    rkeyEnd: t.Optional[str] = None  #: DEPRECATED: The highest sort-ordered rkey to stop at (exclusive).
    rkeyStart: t.Optional[str] = None  #: DEPRECATED: The lowest sort-ordered rkey to start from (exclusive).


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.listRecords`."""

    records: t.List['models.ComAtprotoRepoListRecords.Record']  #: Records.
    cursor: t.Optional[str] = None  #: Cursor.


@dataclass
class Record(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.listRecords`."""

    cid: str  #: Cid.
    uri: str  #: Uri.
    value: 'base.UnknownDict'  #: Value.

    _type: str = 'com.atproto.repo.listRecords#record'
