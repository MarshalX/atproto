##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Optional

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.deleteRecord`.

    Attributes:
        repo: The handle or DID of the repo.
        collection: The NSID of the record collection.
        rkey: The key of the record.
        swapRecord: Compare and swap with the previous record by cid.
        swapCommit: Compare and swap with the previous commit by cid.
    """

    collection: str
    repo: str
    rkey: str
    swapCommit: Optional[str] = None
    swapRecord: Optional[str] = None
