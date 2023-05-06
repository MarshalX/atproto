##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from dataclasses import dataclass

from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


@dataclass
class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.like`.

    Attributes:
        subject: Subject.
        createdAt: Created at.
    """

    createdAt: str
    subject: 'models.ComAtprotoRepoStrongRef.Main'

    _type: str = 'app.bsky.feed.like'
