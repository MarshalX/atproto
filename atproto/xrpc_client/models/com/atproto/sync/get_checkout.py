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

    """Parameters model for :obj:`com.atproto.sync.getCheckout`.

    Attributes:
        did: The DID of the repo.
        commit: The commit to get the checkout from. Defaults to current HEAD.
    """

    did: str
    commit: t.Optional[str] = None


#: Response raw data type.
Response: t.Union[t.Type[str], t.Type[bytes]] = bytes
