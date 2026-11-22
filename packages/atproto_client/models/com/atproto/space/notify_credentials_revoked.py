#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import base, string_formats


class Data(base.DataModelBase):
    """Input data model for :obj:`com.atproto.space.notifyCredentialsRevoked`."""

    credentials: t.List[te.Annotated[str, Field(min_length=1)]] = Field(
        min_length=1, max_length=100
    )  #: The IDs (jti) of the revoked credentials.
    space: string_formats.SpaceRef  #: Space.


class DataDict(t.TypedDict):
    credentials: t.List[te.Annotated[str, Field(min_length=1)]]  #: The IDs (jti) of the revoked credentials.
    space: string_formats.SpaceRef  #: Space.
