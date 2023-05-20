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

    """Parameters model for :obj:`com.atproto.repo.listRecords`.

    Attributes:
        repo: The handle or DID of the repo.
        collection: The NSID of the record type.
        limit: The number of records to return.
        cursor: Cursor.
        rkeyStart: DEPRECATED: The lowest sort-ordered rkey to start from (exclusive).
        rkeyEnd: DEPRECATED: The highest sort-ordered rkey to stop at (exclusive).
        reverse: Reverse the order of the returned records?
    """

    collection: str
    repo: str
    cursor: t.Optional[str] = None
    limit: t.Optional[int] = None
    reverse: t.Optional[bool] = None
    rkeyEnd: t.Optional[str] = None
    rkeyStart: t.Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.listRecords`.

    Attributes:
        cursor: Cursor.
        records: Records.
    """

    records: t.List['models.ComAtprotoRepoListRecords.Record']
    cursor: t.Optional[str] = None


@dataclass
class Record(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.listRecords`.

    Attributes:
        uri: Uri.
        cid: Cid.
        value: Value.
    """

    cid: str
    uri: str
    value: 'base.RecordModelBase'

    _type: str = 'com.atproto.repo.listRecords#record'
