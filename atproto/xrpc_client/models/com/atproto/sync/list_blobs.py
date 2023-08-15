##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.sync.listBlobs`."""

    did: str  #: The DID of the repo.
    earliest: t.Optional[str] = None  #: The earliest commit to start from.
    latest: t.Optional[str] = None  #: The most recent commit.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.sync.listBlobs`."""

    cids: t.List[str]  #: Cids.
