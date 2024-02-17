##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.repo.applyWrites`."""

    repo: str  #: The handle or DID of the repo (aka, current account).
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
    swap_commit: t.Optional[
        str
    ] = None  #: If provided, the entire operation will fail if the current repo commit CID does not match this value. Used to prevent conflicting repo mutations.
    validate_: t.Optional[
        bool
    ] = None  #: Can be set to 'false' to skip Lexicon schema validation of record data, for all operations.


class DataDict(te.TypedDict):
    repo: str  #: The handle or DID of the repo (aka, current account).
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
    swap_commit: te.NotRequired[
        t.Optional[str]
    ]  #: If provided, the entire operation will fail if the current repo commit CID does not match this value. Used to prevent conflicting repo mutations.
    validate: te.NotRequired[
        t.Optional[bool]
    ]  #: Can be set to 'false' to skip Lexicon schema validation of record data, for all operations.


class Create(base.ModelBase):
    """Definition model for :obj:`com.atproto.repo.applyWrites`. Operation which creates a new record."""

    collection: str  #: Collection.
    value: 'UnknownType'  #: Value.
    rkey: t.Optional[str] = Field(default=None, max_length=15)  #: Rkey.

    py_type: te.Literal['com.atproto.repo.applyWrites#create'] = Field(
        default='com.atproto.repo.applyWrites#create', alias='$type', frozen=True
    )


class Update(base.ModelBase):
    """Definition model for :obj:`com.atproto.repo.applyWrites`. Operation which updates an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.
    value: 'UnknownType'  #: Value.

    py_type: te.Literal['com.atproto.repo.applyWrites#update'] = Field(
        default='com.atproto.repo.applyWrites#update', alias='$type', frozen=True
    )


class Delete(base.ModelBase):
    """Definition model for :obj:`com.atproto.repo.applyWrites`. Operation which deletes an existing record."""

    collection: str  #: Collection.
    rkey: str  #: Rkey.

    py_type: te.Literal['com.atproto.repo.applyWrites#delete'] = Field(
        default='com.atproto.repo.applyWrites#delete', alias='$type', frozen=True
    )
