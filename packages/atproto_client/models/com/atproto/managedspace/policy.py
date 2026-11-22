#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Main(base.ModelBase):
    """Definition model for :obj:`com.atproto.managedspace.policy`. Space policy that delegates access decisions to an external app through checkAccess."""

    managing_app: str  #: The `did#serviceId` reference of the managing app.
    publish_policy: t.Optional[bool] = False  #: Publish the policy as a com.atproto.space.policy record in the space.

    py_type: t.Literal['com.atproto.managedspace.policy'] = Field(
        default='com.atproto.managedspace.policy', alias='$type', frozen=True
    )
