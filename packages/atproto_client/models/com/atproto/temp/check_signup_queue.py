##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


import typing as t

from pydantic import Field

from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.temp.checkSignupQueue`."""

    activated: bool  #: Activated.
    estimated_time_ms: t.Optional[int] = Field(default=None, alias='estimatedTimeMs')  #: Estimated time ms.
    place_in_queue: t.Optional[int] = Field(default=None, alias='placeInQueue')  #: Place in queue.
