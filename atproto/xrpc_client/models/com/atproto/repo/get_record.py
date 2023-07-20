##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.getRecord`."""

    collection: str  #: The NSID of the record collection.
    repo: str  #: The handle or DID of the repo.
    rkey: str  #: The key of the record.
    cid: t.Optional[
        str
    ] = None  #: The CID of the version of the record. If not specified, then return the most recent version.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.getRecord`."""

    uri: str  #: Uri.
    value: 'base.UnknownDict'  #: Value.
    cid: t.Optional[str] = None  #: Cid.
