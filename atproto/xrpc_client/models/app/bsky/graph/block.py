##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client.models import base


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.graph.block`."""

    createdAt: str  #: Created at.
    subject: str  #: Subject.

    _type: str = 'app.bsky.graph.block'
