##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Optional

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.getRecord`.

    Attributes:
        repo: The handle or DID of the repo.
        collection: The NSID of the record collection.
        rkey: The key of the record.
        cid: The CID of the version of the record. If not specified, then return the most recent version.
    """

    collection: str
    repo: str
    rkey: str
    cid: Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.getRecord`.

    Attributes:
        uri: Uri.
        cid: Cid.
        value: Value.
    """

    uri: str
    value: 'base.RecordModelBase'
    cid: Optional[str] = None
