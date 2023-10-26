##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.graph.listitem`."""

    created_at: str = Field(alias='createdAt')  #: Created at.
    list: str  #: List.
    subject: str  #: Subject.

    py_type: te.Literal['app.bsky.graph.listitem'] = Field(
        default='app.bsky.graph.listitem', alias='$type', frozen=True
    )
