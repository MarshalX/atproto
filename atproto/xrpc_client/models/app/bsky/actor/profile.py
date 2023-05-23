##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t
from dataclasses import dataclass

from atproto.xrpc_client.models import base
from atproto.xrpc_client.models.blob_ref import BlobRef


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.actor.profile`."""

    avatar: t.Optional[BlobRef] = None  #: Avatar.
    banner: t.Optional[BlobRef] = None  #: Banner.
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.

    _type: str = 'app.bsky.actor.profile'
