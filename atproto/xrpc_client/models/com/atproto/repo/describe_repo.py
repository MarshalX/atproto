##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.describeRepo`.

    Attributes:
        repo: The handle or DID of the repo.
    """

    repo: str


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.describeRepo`.

    Attributes:
        handle: Handle.
        did: Did.
        didDoc: Did doc.
        collections: Collections.
        handleIsCorrect: Handle is correct.
    """

    collections: List[str]
    did: str
    didDoc: 'base.RecordModelBase'
    handle: str
    handleIsCorrect: bool
