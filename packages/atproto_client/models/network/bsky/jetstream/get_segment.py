#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te

from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`network.bsky.jetstream.getSegment`."""

    name: str  #: The segment filename, e.g. seg_000000002a.jss.


class ParamsDict(t.TypedDict):
    name: str  #: The segment filename, e.g. seg_000000002a.jss.


#: Response raw data type.
Response: te.TypeAlias = bytes
