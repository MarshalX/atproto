##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
    from atproto.xrpc_client.models.blob_ref import BlobRef
from atproto.xrpc_client.models import base


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.actor.profile`."""

    avatar: t.Optional['BlobRef'] = None  #: Avatar.
    banner: t.Optional['BlobRef'] = None  #: Banner.
    description: t.Optional[str] = None  #: Description.
    displayName: t.Optional[str] = None  #: Display name.
    labels: t.Optional[t.Union['models.ComAtprotoLabelDefs.SelfLabels', 't.Dict[str, t.Any]']] = None  #: Labels.

    _type: str = 'app.bsky.actor.profile'
