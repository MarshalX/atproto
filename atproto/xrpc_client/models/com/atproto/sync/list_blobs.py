##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.listBlobs`."""

    did: str  #: The DID of the repo.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = Field(default=500, ge=1, le=1000)  #: Limit.
    since: t.Optional[str] = None  #: Optional revision of the repo to list blobs since.


class ParamsDict(te.TypedDict):
    did: str  #: The DID of the repo.
    cursor: te.NotRequired[t.Optional[str]]  #: Cursor.
    limit: te.NotRequired[t.Optional[int]]  #: Limit.
    since: te.NotRequired[t.Optional[str]]  #: Optional revision of the repo to list blobs since.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listBlobs`."""

    cids: t.List[str]  #: Cids.
    cursor: t.Optional[str] = None  #: Cursor.
