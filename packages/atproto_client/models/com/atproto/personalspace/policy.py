#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Main(base.ModelBase):
    """Definition model for :obj:`com.atproto.personalspace.policy`. Space policy for personal data that only the space authority and authorized apps can read, such as bookmarks or drafts."""

    py_type: t.Literal['com.atproto.personalspace.policy'] = Field(
        default='com.atproto.personalspace.policy', alias='$type', frozen=True
    )
