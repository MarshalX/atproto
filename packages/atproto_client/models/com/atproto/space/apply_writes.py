#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.applyWrites`."""

    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    writes: t.List[
        te.Annotated[
            t.Union[
                'models.ComAtprotoSpaceApplyWrites.Create',
                'models.ComAtprotoSpaceApplyWrites.Update',
                'models.ComAtprotoSpaceApplyWrites.Delete',
            ],
            Field(discriminator='py_type'),
        ]
    ]  #: Writes.
    validate_: t.Optional[bool] = (
        None  #: Can be set to 'false' to skip Lexicon schema validation of record data across all operations, 'true' to require it, or leave unset to validate only for known Lexicons.
    )


class DataDict(t.TypedDict):
    repo: string_formats.Did  #: Repo.
    space: string_formats.SpaceRef  #: Space.
    writes: t.List[
        te.Annotated[
            t.Union[
                'models.ComAtprotoSpaceApplyWrites.Create',
                'models.ComAtprotoSpaceApplyWrites.Update',
                'models.ComAtprotoSpaceApplyWrites.Delete',
            ],
            Field(discriminator='py_type'),
        ]
    ]  #: Writes.
    validate_: te.NotRequired[
        t.Optional[bool]
    ]  #: Can be set to 'false' to skip Lexicon schema validation of record data across all operations, 'true' to require it, or leave unset to validate only for known Lexicons.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.space.applyWrites`."""

    results: t.Optional[
        t.List[
            te.Annotated[
                t.Union[
                    'models.ComAtprotoSpaceApplyWrites.CreateResult',
                    'models.ComAtprotoSpaceApplyWrites.UpdateResult',
                    'models.ComAtprotoSpaceApplyWrites.DeleteResult',
                ],
                Field(discriminator='py_type'),
            ]
        ]
    ] = None  #: Results.


class Create(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`. Operation which creates a new record."""

    collection: string_formats.Nsid  #: Collection.
    value: 'UnknownType'  #: Value.
    rkey: t.Optional[string_formats.RecordKey] = None  #: Rkey.

    py_type: t.Literal['com.atproto.space.applyWrites#create'] = Field(
        default='com.atproto.space.applyWrites#create', alias='$type', frozen=True
    )


class Update(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`. Operation which updates an existing record."""

    collection: string_formats.Nsid  #: Collection.
    rkey: string_formats.RecordKey  #: Rkey.
    value: 'UnknownType'  #: Value.

    py_type: t.Literal['com.atproto.space.applyWrites#update'] = Field(
        default='com.atproto.space.applyWrites#update', alias='$type', frozen=True
    )


class Delete(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`. Operation which deletes an existing record."""

    collection: string_formats.Nsid  #: Collection.
    rkey: string_formats.RecordKey  #: Rkey.

    py_type: t.Literal['com.atproto.space.applyWrites#delete'] = Field(
        default='com.atproto.space.applyWrites#delete', alias='$type', frozen=True
    )


class CreateResult(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`."""

    cid: string_formats.Cid  #: Cid.
    uri: string_formats.AtUri  #: Uri.
    validation_status: t.Optional[t.Union[t.Literal['valid', 'unknown'], str]] = None  #: Validation status.

    py_type: t.Literal['com.atproto.space.applyWrites#createResult'] = Field(
        default='com.atproto.space.applyWrites#createResult', alias='$type', frozen=True
    )


class UpdateResult(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`."""

    cid: string_formats.Cid  #: Cid.
    uri: string_formats.AtUri  #: Uri.
    validation_status: t.Optional[t.Union[t.Literal['valid', 'unknown'], str]] = None  #: Validation status.

    py_type: t.Literal['com.atproto.space.applyWrites#updateResult'] = Field(
        default='com.atproto.space.applyWrites#updateResult', alias='$type', frozen=True
    )


class DeleteResult(base.ModelBase):
    """Definition model for :obj:`com.atproto.space.applyWrites`."""

    py_type: t.Literal['com.atproto.space.applyWrites#deleteResult'] = Field(
        default='com.atproto.space.applyWrites#deleteResult', alias='$type', frozen=True
    )
