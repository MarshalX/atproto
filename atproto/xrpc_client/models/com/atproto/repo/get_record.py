##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base, unknown_type


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.getRecord`."""

    collection: str  #: The NSID of the record collection.
    repo: str  #: The handle or DID of the repo.
    rkey: str  #: The key of the record.
    cid: t.Optional[
        str
    ] = None  #: The CID of the version of the record. If not specified, then return the most recent version.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.getRecord`."""

    uri: str  #: Uri.
    value: 'unknown_type.UnknownRecordTypePydantic'  #: Value.
    cid: t.Optional[str] = None  #: Cid.
