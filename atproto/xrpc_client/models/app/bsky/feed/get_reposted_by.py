##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Params(base.ParamsModelBase):

    """Parameters model for :obj:`app.bsky.feed.getRepostedBy`."""

    uri: str  #: Uri.
    cid: t.Optional[str] = None  #: Cid.
    cursor: t.Optional[str] = None  #: Cursor.
    limit: t.Optional[int] = None  #: Limit.


@dataclass
class Response(base.ResponseModelBase):

    """Output data model for :obj:`app.bsky.feed.getRepostedBy`."""

    repostedBy: t.List['models.AppBskyActorDefs.ProfileView']  #: Reposted by.
    uri: str  #: Uri.
    cid: t.Optional[str] = None  #: Cid.
    cursor: t.Optional[str] = None  #: Cursor.
