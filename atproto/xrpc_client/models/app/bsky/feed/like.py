##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    from atproto.xrpc_client import models
from atproto.xrpc_client.models import base


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.feed.like`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    subject: 'models.ComAtprotoRepoStrongRef.Main'  #: Subject.

    py_type: te.Literal['app.bsky.feed.like'] = Field(default='app.bsky.feed.like', alias='$type', frozen=True)
