##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import List, Optional

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.listBlobs`.

    Attributes:
        did: The DID of the repo.
        latest: The most recent commit.
        earliest: The earliest commit to start from.
    """

    did: str
    earliest: Optional[str] = None
    latest: Optional[str] = None


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listBlobs`.

    Attributes:
        cids: Cids.
    """

    cids: List[str]
