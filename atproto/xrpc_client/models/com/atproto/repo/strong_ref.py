##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing_extensions as te
from pydantic import Field

from atproto.xrpc_client.models import base


class Main(base.ModelBase):

    """Definition model for :obj:`com.atproto.repo.strongRef`."""

    cid: str  #: Cid.
    uri: str  #: Uri.

    py_type: te.Literal['com.atproto.repo.strongRef'] = Field(
        default='com.atproto.repo.strongRef', alias='$type', frozen=True
    )
