#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.video.uploadPart`."""

    job_id: str = Field(min_length=1, max_length=256)  #: Job id.
    part_number: int = Field(ge=1)  #: Part number.


class ParamsDict(t.TypedDict):
    job_id: str  #: Job id.
    part_number: int  #: Part number.


#: Data raw data type.
Data: te.TypeAlias = bytes


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.video.uploadPart`."""

    part_number: int = Field(ge=1)  #: Part number.
    size_bytes: int  #: Size bytes.
