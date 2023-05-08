##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

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
    writes: List[
        Union[
            'models.ComAtprotoRepoApplyWrites.Create',
            'models.ComAtprotoRepoApplyWrites.Update',
            'models.ComAtprotoRepoApplyWrites.Delete',
            'Dict[str, Any]',
        ]
    ]
    swapCommit: Optional[str] = None
    validate: Optional[bool] = None


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
    rkey: Optional[str] = None


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


@dataclass
class Delete(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Delete an existing record.

    Attributes:
        collection: Collection.
        rkey: Rkey.
    """

    collection: str
    rkey: str
