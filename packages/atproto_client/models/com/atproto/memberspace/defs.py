#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base, string_formats


class Member(base.ModelBase):
    """Definition model for :obj:`com.atproto.memberspace.defs`."""

    did: string_formats.Did  #: Did.
    read: bool  #: Read.
    write: bool  #: Write.

    py_type: t.Literal['com.atproto.memberspace.defs#member'] = Field(
        default='com.atproto.memberspace.defs#member', alias='$type', frozen=True
    )
