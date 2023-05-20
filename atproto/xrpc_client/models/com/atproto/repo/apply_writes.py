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
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.applyWrites`.

    Attributes:
        repo: The handle or DID of the repo.
        validate: Validate the records?
        writes: Writes.
        swapCommit: Swap commit.
    """

    repo: str
    writes: t.List[
        t.Union[
            'models.ComAtprotoRepoApplyWrites.Create',
            'models.ComAtprotoRepoApplyWrites.Update',
            'models.ComAtprotoRepoApplyWrites.Delete',
            't.Dict[str, t.Any]',
        ]
    ]
    swapCommit: t.Optional[str] = None
    validate: t.Optional[bool] = None


@dataclass
class Create(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Create a new record.

    Attributes:
        collection: Collection.
        rkey: Rkey.
        value: Value.
    """

    collection: str
    value: 'base.RecordModelBase'
    rkey: t.Optional[str] = None

    _type: str = 'com.atproto.repo.applyWrites#create'


@dataclass
class Update(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Update an existing record.

    Attributes:
        collection: Collection.
        rkey: Rkey.
        value: Value.
    """

    collection: str
    rkey: str
    value: 'base.RecordModelBase'

    _type: str = 'com.atproto.repo.applyWrites#update'


@dataclass
class Delete(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Delete an existing record.

    Attributes:
        collection: Collection.
        rkey: Rkey.
    """

    collection: str
    rkey: str

    _type: str = 'com.atproto.repo.applyWrites#delete'
