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
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.repo.listMissingBlobs`."""

    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=500, ge=1, le=1000)  #: Limit.


class ParamsDict(te.TypedDict):
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.repo.listMissingBlobs`."""

    blobs: t.List['models.ComAtprotoRepoListMissingBlobs.RecordBlob']  #: Blobs.
    cursor: t.Optional[str] = None  #: Cursor.


class RecordBlob(base.ModelBase):
    """Definition model for :obj:`com.atproto.repo.listMissingBlobs`."""

    cid: str  #: Cid.
    record_uri: str  #: Record uri.

    py_type: te.Literal['com.atproto.repo.listMissingBlobs#recordBlob'] = Field(
        default='com.atproto.repo.listMissingBlobs#recordBlob', alias='$type', frozen=True
    )
