##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Data(base.DataModelBase):

    """Input data model for :obj:`com.atproto.repo.deleteRecord`."""

    collection: str  #: The NSID of the record collection.
    repo: str  #: The handle or DID of the repo.
    rkey: str  #: The key of the record.
    swapCommit: t.Optional[str] = None  #: Compare and swap with the previous commit by cid.
    swapRecord: t.Optional[str] = None  #: Compare and swap with the previous record by cid.
