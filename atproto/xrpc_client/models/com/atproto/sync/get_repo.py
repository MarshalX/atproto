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

    """Parameters model for :obj:`com.atproto.sync.getRepo`."""

    did: str  #: The DID of the repo.
    earliest: t.Optional[str] = None  #: The earliest commit in the commit range (not inclusive).
    latest: t.Optional[str] = None  #: The latest commit in the commit range (inclusive).


#: Response raw data type.
Response: t.Union[t.Type[str], t.Type[bytes]] = bytes
