#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base, string_formats


class Main(base.ModelBase):
    """Definition model for :obj:`com.atproto.memberspace.policy`. Space policy that grants access based on a member list."""

    allowed_apps: t.Optional[t.List[string_formats.Uri]] = (
        None  #: If set, only these apps (by OAuth client ID) may read the space.
    )
    public_read: t.Optional[bool] = (
        False  #: If true, anyone may read the space. Otherwise, only members with read access.
    )
    public_write: t.Optional[bool] = (
        False  #: If true, any account's writes are tracked in the writer set, except members without write access. Otherwise, only members with write access.
    )
    publish_members: t.Optional[bool] = (
        False  #: Publish the member list as com.atproto.memberspace.member records in the space.
    )
    publish_policy: t.Optional[bool] = False  #: Publish the policy as a com.atproto.space.policy record in the space.

    py_type: t.Literal['com.atproto.memberspace.policy'] = Field(
        default='com.atproto.memberspace.policy', alias='$type', frozen=True
    )
