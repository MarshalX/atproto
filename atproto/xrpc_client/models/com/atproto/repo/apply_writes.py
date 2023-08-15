##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.applyWrites`."""

    repo: str  #: The handle or DID of the repo.
    writes: t.List[
        t.Union[
            'models.ComAtprotoRepoApplyWrites.Create',
            'models.ComAtprotoRepoApplyWrites.Update',
            'models.ComAtprotoRepoApplyWrites.Delete',
            't.Dict[str, t.Any]',
        ]
    ]  #: Writes.
    swapCommit: t.Optional[str] = None  #: Swap commit.
    validateFixMe: t.Optional[bool] = None  #: Validate the records?


class Create(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Create a new record."""

    collection: str  #: Collection.
    value: 'base.UnknownDict'  #: Value.
    rkey: t.Optional[str] = None  #: Rkey.

    _type: str = 'com.atproto.repo.applyWrites#create'


class Update(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Update an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.
    value: 'base.UnknownDict'  #: Value.

    _type: str = 'com.atproto.repo.applyWrites#update'


class Delete(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Delete an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.

    _type: str = 'com.atproto.repo.applyWrites#delete'
