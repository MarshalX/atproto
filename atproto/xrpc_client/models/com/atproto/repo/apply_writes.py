##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base, unknown_type


class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.applyWrites`."""

    repo: str  #: The handle or DID of the repo.
    writes: t.List[
        te.Annotated[
            t.Union[
                'models.ComAtprotoRepoApplyWrites.Create',
                'models.ComAtprotoRepoApplyWrites.Update',
                'models.ComAtprotoRepoApplyWrites.Delete',
            ],
            Field(discriminator='py_type'),
        ]
    ]  #: Writes.
    swapCommit: t.Optional[str] = None  #: Swap commit.
    validateAliasMe: t.Optional[bool] = None  #: Validate the records?


class Create(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Create a new record."""

    collection: str  #: Collection.
    value: 'unknown_type.UnknownRecordTypePydantic'  #: Value.
    rkey: t.Optional[str] = None  #: Rkey.

    py_type: te.Literal['com.atproto.repo.applyWrites#create'] = Field(
        default='com.atproto.repo.applyWrites#create', alias='$type'
    )


class Update(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Update an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.
    value: 'unknown_type.UnknownRecordTypePydantic'  #: Value.

    py_type: te.Literal['com.atproto.repo.applyWrites#update'] = Field(
        default='com.atproto.repo.applyWrites#update', alias='$type'
    )


class Delete(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.applyWrites`. Delete an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.

    py_type: te.Literal['com.atproto.repo.applyWrites#delete'] = Field(
        default='com.atproto.repo.applyWrites#delete', alias='$type'
    )
