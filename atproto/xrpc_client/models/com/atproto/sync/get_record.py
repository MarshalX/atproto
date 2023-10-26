##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.getRecord`."""

    collection: str  #: Collection.
    did: str  #: The DID of the repo.
    rkey: str  #: Rkey.
    commit: t.Optional[str] = None  #: An optional past commit CID.


class ParamsDict(te.TypedDict):
    collection: str  #: Collection.
    did: str  #: The DID of the repo.
    rkey: str  #: Rkey.
    commit: te.NotRequired[t.Optional[str]]  #: An optional past commit CID.


#: Response raw data type.
Response: te.TypeAlias = bytes
