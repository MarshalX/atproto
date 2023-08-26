##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base, unknown_type


class Params(base.ParamsModelBase):

    """Parameters model for :obj:`com.atproto.repo.describeRepo`."""

    repo: str  #: The handle or DID of the repo.


class Response(base.ResponseModelBase):

    """Output data model for :obj:`com.atproto.repo.describeRepo`."""

    collections: t.List[str]  #: Collections.
    did: str  #: Did.
    didDoc: 'unknown_type.UnknownType'  #: Did doc.
    handle: str  #: Handle.
    handleIsCorrect: bool  #: Handle is correct.
