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
    """Parameters model for :obj:`network.bsky.jetstream.getZstdDictionary`."""

    id: te.Annotated[t.Optional[int], Field(ge=1)] = (
        None  #: The zstd dictionary ID to fetch. Omitted: the server's current dictionary.
    )


class ParamsDict(t.TypedDict):
    id: te.NotRequired[t.Optional[int]]  #: The zstd dictionary ID to fetch. Omitted: the server's current dictionary.


#: Response raw data type.
Response: te.TypeAlias = bytes
