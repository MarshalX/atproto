##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownType
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`com.atproto.repo.describeRepo`."""

    repo: str  #: The handle or DID of the repo.


class ParamsDict(te.TypedDict):
    repo: str  #: The handle or DID of the repo.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.repo.describeRepo`."""

    collections: t.List[str]  #: List of all the collections (NSIDs) for which this repo contains at least one record.
    did: str  #: Did.
    did_doc: 'UnknownType'  #: The complete DID document for this account.
    handle: str  #: Handle.
    handle_is_correct: bool  #: Indicates if handle is currently valid (resolves bi-directionally).
