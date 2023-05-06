##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass
from typing import Type, Union

from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.getBlob`.

    Attributes:
        did: The DID of the repo.
        cid: The CID of the blob to fetch.
    """

    cid: str
    did: str


#: Response raw data type.
Response: Union[Type[str], Type[bytes]] = bytes
