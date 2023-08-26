##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

if t.TYPE_CHECKING:
    pass
from atproto.xrpc_client.models import base


class Main(base.RecordModelBase):

    """Record model for :obj:`app.bsky.graph.listitem`."""

    createdAt: str  #: Created at.
    list: str  #: List.
    subject: str  #: Subject.

    py_type: te.Literal['app.bsky.graph.listitem'] = Field(default='app.bsky.graph.listitem', alias='$type')
